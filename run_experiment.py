"""
Main experiment runner for Spotlighting evaluation.

Usage:
    python run_experiment.py                  # Run all experiments
    python run_experiment.py --naive-only     # Run only naive attack experiments
    python run_experiment.py --adaptive-only  # Run only adaptive attack experiments
    python run_experiment.py --quick          # Quick run with 10 docs
"""

import argparse
import random
import time
from datetime import datetime

from config import OLLAMA_MODEL, NUM_ATTACK_DOCS
from attack_corpus import generate_naive_corpus, generate_clean_corpus
from adaptive_attacks import generate_adaptive_corpus, ADAPTIVE_ATTACK_TYPES
from spotlighting import DEFENSE_METHODS
from evaluate import (
    evaluate_defense,
    evaluate_utility,
    print_results_table,
    save_results,
    query_ollama,
)


def check_ollama_connection():
    """Verify Ollama is running and the model is available."""
    print(f"Checking Ollama connection (model: {OLLAMA_MODEL})...")
    response = query_ollama("You are a test.", "Say 'OK' if you can hear me.")
    if "[ERROR]" in response or "[CONNECTION_ERROR]" in response:
        print("Failed to connect to Ollama. Exiting.")
        print("Make sure Ollama is running: `ollama serve`")
        print(f"And the model is pulled: `ollama pull {OLLAMA_MODEL}`")
        return False
    print(f"Connection OK. Model response: {response[:50]}")
    return True


def run_naive_experiments(n_docs: int, verbose: bool = True) -> dict:
    """Run all defense methods against naive attacks."""
    print("\n" + "=" * 70)
    print("EXPERIMENT 1: Naive Attacks vs. All Defense Methods")
    print("=" * 70)

    random.seed(42)  # Reproducibility
    corpus = generate_naive_corpus(n_docs)
    print(f"Generated {len(corpus)} naive attack documents.\n")

    all_results = {}
    for defense_name, defense_fn in DEFENSE_METHODS.items():
        print(f"\nTesting defense: {defense_name}")
        print("-" * 40)
        result = evaluate_defense(corpus, defense_fn, verbose=verbose)
        all_results[defense_name] = result
        print(f"  ASR: {result['asr_pct']}")

    print_results_table(all_results)
    return all_results


def run_adaptive_experiments(n_docs: int, verbose: bool = True) -> dict:
    """Run adaptive attacks against each relevant defense method.

    For each (attack, defense) pair, we regenerate the corpus with the same
    seed so the comparison is fair across defenses. This is intentional:
    we want to compare how the SAME corpus performs against different defenses.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 2: Adaptive Attacks vs. Targeted Defense Methods")
    print("=" * 70)

    # Each adaptive attack is tested against the defense it specifically
    # targets, plus optionally against the strongest defense for comparison.
    attack_defense_pairs = [
        # Each adaptive attack against the defense it was designed for:
        ("delimiter_aware", "delimiter"),
        ("datamark_mimicking", "datamarking"),
        ("pseudo_decoded", "encoding"),
        ("nested_base64", "encoding"),
        # Defense-agnostic attacks tested against the strongest defenses:
        ("social_engineering", "datamarking"),
        ("social_engineering", "encoding"),
        ("context_stuffing", "datamarking"),
        ("context_stuffing", "encoding"),
    ]

    all_results = {}
    for attack_type, defense_name in attack_defense_pairs:
        label = f"{attack_type} → {defense_name}"
        print(f"\nTesting: {label}")
        print("-" * 40)

        random.seed(42)
        corpus = generate_adaptive_corpus(attack_type, n_docs)
        defense_fn = DEFENSE_METHODS[defense_name]
        result = evaluate_defense(corpus, defense_fn, verbose=verbose)
        all_results[label] = result
        print(f"  ASR: {result['asr_pct']}")

    print_results_table(all_results)
    return all_results


def run_utility_test(n_docs: int, verbose: bool = True) -> dict:
    """Quantify whether each defense preserves faithful summarization.

    Runs every defense over a corpus of CLEAN documents (no injection) and
    scores each summary against the source document's own keywords. This is
    what exposes the encoding confound: a defense can show 0% ASR simply
    because the model cannot read the document at all, which also drives its
    utility to ~0%. ASR is only meaningful alongside this number.
    """
    print("\n" + "=" * 70)
    print("EXPERIMENT 3: Utility Test (Clean Documents)")
    print("=" * 70)

    clean_corpus = generate_clean_corpus(n_docs)
    for doc in clean_corpus:
        doc["position"] = "none"  # match the stored result schema
    print(f"Generated {len(clean_corpus)} clean documents.")
    print("Scoring whether each defense still produces faithful summaries...\n")

    all_results = {}
    for defense_name, defense_fn in DEFENSE_METHODS.items():
        print(f"\nTesting defense (utility): {defense_name}")
        print("-" * 40)
        result = evaluate_utility(clean_corpus, defense_fn, verbose=verbose)
        all_results[defense_name] = result
        print(f"  Utility: {result['utility_pct']}")

    print_results_table(all_results, metric_label="Utility")
    return all_results


def main():
    parser = argparse.ArgumentParser(description="Spotlighting Experiment Runner")
    parser.add_argument("--naive-only", action="store_true",
                        help="Run only naive attack experiments")
    parser.add_argument("--adaptive-only", action="store_true",
                        help="Run only adaptive attack experiments")
    parser.add_argument("--utility-only", action="store_true",
                        help="Run only utility tests")
    parser.add_argument("--quick", action="store_true",
                        help="Quick run with 10 documents")
    parser.add_argument("--verbose", action="store_true", default=True,
                        help="Print per-document results")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress per-document output")
    args = parser.parse_args()

    if args.quiet:
        args.verbose = False

    n_docs = 10 if args.quick else NUM_ATTACK_DOCS

    print(f"{'='*70}")
    print(f"Spotlighting Defense Evaluation")
    print(f"Model: {OLLAMA_MODEL}")
    print(f"Documents per experiment: {n_docs}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")

    if not check_ollama_connection():
        return

    all_experiment_results = {}

    if args.naive_only:
        all_experiment_results["naive"] = run_naive_experiments(n_docs, args.verbose)
    elif args.adaptive_only:
        all_experiment_results["adaptive"] = run_adaptive_experiments(n_docs, args.verbose)
    elif args.utility_only:
        all_experiment_results["utility"] = run_utility_test(n_docs, args.verbose)
    else:
        # Run everything
        all_experiment_results["naive"] = run_naive_experiments(n_docs, args.verbose)
        all_experiment_results["adaptive"] = run_adaptive_experiments(n_docs, args.verbose)
        all_experiment_results["utility"] = run_utility_test(n_docs, args.verbose)

    # Save results
    if all_experiment_results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        all_experiment_results["meta"] = {
            "model": OLLAMA_MODEL,
            "n_docs": n_docs,
            "timestamp": timestamp,
        }
        filename = f"results_{timestamp}.json"
        save_results(all_experiment_results, filename)

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()