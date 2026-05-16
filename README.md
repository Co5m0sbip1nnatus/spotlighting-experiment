# Spotlighting Defense Evaluation

Experimental evaluation of [Spotlighting](https://arxiv.org/abs/2403.14720) (Hines et al., 2024) as a defense against indirect prompt injection attacks. Companion code for the blog post: *Implementing and Breaking Spotlighting*.

## What This Does

Implements three Spotlighting defenses (Delimiting, Datamarking, Encoding) and evaluates them against:

- **Naive attacks** — generic injection payloads
- **Adaptive attacks** — payloads designed with knowledge of each specific defense

Measures Attack Success Rate (ASR) and produces charts for analysis.

## Setup

1. Install [Ollama](https://ollama.com) and pull a model:
   ```bash
   ollama pull llama3.1:8b
   ```

2. Install Python dependencies:
   ```bash
   pip install requests matplotlib
   ```

3. (Optional) Edit `config.py` to change the model or experiment parameters.

## Running Experiments

```bash
# Quick test (10 documents per condition, ~10 min)
python run_experiment.py --quick

# Full run (50 documents per condition, ~1 hour)
python run_experiment.py

# Only naive attack experiments
python run_experiment.py --naive-only

# Only adaptive attack experiments
python run_experiment.py --adaptive-only

# Only utility test on clean documents
python run_experiment.py --utility-only
```

Results are written to `results/results_<timestamp>.json`.

## Generating Charts

After running an experiment, generate the charts used in the blog post:

```bash
cd charts
python chart1.py ../results/results_20260516_114446.json
python chart2.py ../results/results_20260516_114446.json
python chart3.py ../results/results_20260516_114446.json
```

Each script reads ASR data from the JSON and saves a PNG.

## Project Structure

```
.
├── config.py            # Model and experiment settings
├── attack_corpus.py     # Benign documents + naive attack payloads
├── adaptive_attacks.py  # Six adaptive attack variants
├── spotlighting.py      # Defense implementations
├── evaluate.py          # Ollama interaction + ASR scoring
├── run_experiment.py    # Main experiment runner
├── charts/              # Plotting scripts for blog post figures
└── results/             # Experiment output (JSON)
```

## Reference Results

`results/results_20260516_114446.json` contains the full results from the blog post (Llama 3.1 8B, n=50 per condition). Use it as a sanity check that your local setup reproduces the headline numbers.

## References

- Hines, K., Lopez, G., Hall, M., Zarfati, F., Zunger, Y., Kiciman, E. (2024). *Defending Against Indirect Prompt Injection Attacks With Spotlighting*. [arXiv:2403.14720](https://arxiv.org/abs/2403.14720)
