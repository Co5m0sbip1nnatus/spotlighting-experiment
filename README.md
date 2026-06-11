# Spotlighting Defense Evaluation

Experimental evaluation of [Spotlighting](https://arxiv.org/abs/2403.14720) (Hines et al., 2024) as a defense against indirect prompt injection attacks. Companion code for the blog post: *Implementing and Breaking Spotlighting*.

## What This Does

Implements three Spotlighting defenses (Delimiting, Datamarking, Encoding) and evaluates them against:

- **Naive attacks** — generic injection payloads
- **Adaptive attacks** — payloads designed with knowledge of each specific defense

Measures **Attack Success Rate (ASR)** *and* **Utility** (faithful-summary rate on clean
documents) and produces charts for analysis.

> ### ⚠️ Read ASR together with Utility
>
> A defense can show a low ASR for the wrong reason: if the model cannot read the
> document at all, the injection fails — but so does the legitimate task. This is
> exactly what happens with **Encoding** on a model that cannot decode base64.
>
> On **Llama 3.1 8B**, Encoding reports **0% ASR** — but its **utility is only 2%**:
> the model never decodes the document, it just hallucinates or echoes the ciphertext.
> The "perfect defense" is a broken pipeline, not protection. On **Qwen2.5 14B**, which
> *can* decode base64, utility recovers to **62%** and Encoding still holds at **4% ASR** —
> i.e. it is a *genuine* defense there, at a real utility cost. **Never quote an ASR
> number without its utility number next to it.** See [Reference Results](#reference-results).

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

The utility test is quantitative: each summary of a clean document is scored for
faithfulness (does it mention the source document's own keywords?), so Encoding's
utility collapse is measured, not just eyeballed. Utility results are saved under the
`utility` key alongside `naive`/`adaptive`.

Results are written to `results/results_<timestamp>.json`, which also records run
metadata (`meta.model`, `meta.n_docs`) so cross-model runs are self-documenting.

To run against a different model without editing `config.py`, set `OLLAMA_MODEL`:

```bash
OLLAMA_MODEL=qwen2.5:14b python run_experiment.py
```

## Generating Charts

After running an experiment, generate the charts used in the blog post:

```bash
cd charts
python chart1.py ../results/results_20260516_114446.json
python chart2.py ../results/results_20260516_114446.json
python chart3.py ../results/results_20260516_114446.json
```

Each script reads ASR data from the JSON and saves a PNG.

### Cross-model comparison charts

`chart_compare.py` contrasts two (or more) models — it draws the ASR-vs-utility story
for Encoding and a per-defense naive-ASR comparison. Each model's data may span several
result files (e.g. a naive run plus a separate utility run); list them comma-separated:

```bash
cd charts
python chart_compare.py \
  "Llama 3.1 8B:../results/results_20260516_114446.json,../results/results_20260610_012625.json" \
  "Qwen2.5 14B:../results/results_20260610_020410.json,../results/results_20260610_022525.json"
```

This produces `chart_compare_encoding.png` (the encoding confound) and
`chart_compare_naive_asr.png` (naive ASR by defense and model).

## Project Structure

```
.
├── config.py            # Model and experiment settings
├── attack_corpus.py     # Benign documents + naive attack payloads
├── adaptive_attacks.py  # Six adaptive attack variants
├── spotlighting.py      # Defense implementations
├── evaluate.py          # Ollama interaction + ASR and utility scoring
├── run_experiment.py    # Main experiment runner
├── charts/              # Plotting scripts (incl. chart_compare.py, cross-model)
└── results/             # Experiment output (JSON)
```

## Reference Results

All committed reference runs use n=50 per condition.

| File | Model | Contents |
|------|-------|----------|
| `results_20260516_114446.json` | Llama 3.1 8B | Original naive + adaptive ASR (no utility) |
| `results_20260610_012625.json` | Llama 3.1 8B | Utility test — exposes the Encoding confound (encoding utility 2%) |
| `results_20260610_020410.json` | Qwen2.5 14B | Naive ASR |
| `results_20260610_022525.json` | Qwen2.5 14B | Utility test (encoding utility 62%) |

Headline numbers, naive attacks:

| Defense | 8B ASR | 8B Utility | 14B ASR | 14B Utility |
|---|---|---|---|---|
| No Defense | 70% | 98% | 100% | 100% |
| Instructions Only | 40% | 100% | 94% | 100% |
| Delimiter | 60% | 100% | 100% | 100% |
| Datamarking | 16% | 100% | 88% | 100% |
| **Encoding** | **0%** | **2%** | **4%** | **62%** |

Two takeaways:

1. **Encoding's 8B "0% ASR" is a confound** (utility 2%), not a defense. On 14B, where the
   model can decode base64, utility recovers to 62% and Encoding still holds at 4% ASR —
   a genuine defense at a real utility cost.
2. **The plaintext defenses are far weaker on 14B** (e.g. Datamarking 16% → 88%). Caveat:
   this comparison changes both model *size* and *family* (Llama 3.1 → Qwen 2.5), so the
   shift cannot be attributed to capacity alone — Qwen2.5 14B is simply more willing to
   follow embedded instructions. A clean capacity curve would need same-family models.

## References

- Hines, K., Lopez, G., Hall, M., Zarfati, F., Zunger, Y., Kiciman, E. (2024). *Defending Against Indirect Prompt Injection Attacks With Spotlighting*. [arXiv:2403.14720](https://arxiv.org/abs/2403.14720)
