"""
Comparison charts: model capacity vs. the encoding-defense confound.

Produces two figures that tell the story behind the encoding result:

  1. chart_compare_encoding.png
       For the encoding defense, plots Naive Attack ASR side-by-side with
       Utility (faithful-summary rate) for each model. This is the headline:
       on a model that cannot decode base64, ASR is ~0% ONLY because utility
       is also ~0% (the model never reads the document). As model capacity
       grows and base64 decoding works, utility recovers and the TRUE attack
       surface of encoding becomes visible.

  2. chart_compare_naive_asr.png
       Naive ASR for every defense method, grouped by model.

Each model's data may be spread across several result JSON files (e.g. one
file with naive/adaptive results and a separate utility-only file); list them
comma-separated and they are merged (a section present in any file is used).

Usage:
    python chart_compare.py "Llama 3.1 8B:a.json,b.json" "Qwen2.5 14B:c.json"
"""
import json
import sys
import matplotlib.pyplot as plt
import numpy as np

BG = "#FAFBFC"
DEFENSE_ORDER = ["no_defense", "instructions_only", "delimiter", "datamarking", "encoding"]
DEFENSE_LABEL = {
    "no_defense": "No Defense",
    "instructions_only": "Instructions\nOnly",
    "delimiter": "Delimiter",
    "datamarking": "Datamarking",
    "encoding": "Encoding",
}
# One color per model, applied across both charts for consistency.
MODEL_COLORS = ["#9CA3AF", "#6366F1", "#10B981", "#F59E0B"]


def merge_files(paths):
    """Merge several result JSONs into one dict; later files fill missing keys."""
    merged = {}
    for path in paths:
        with open(path.strip()) as f:
            data = json.load(f)
        for section, value in data.items():
            merged.setdefault(section, value)
    return merged


def parse_models(argv):
    """Parse 'Label:file1,file2' arguments into [(label, merged_dict), ...]."""
    models = []
    for arg in argv:
        label, _, files = arg.partition(":")
        if not files:
            raise SystemExit(f"Bad argument (need 'Label:file.json'): {arg}")
        models.append((label, merge_files(files.split(","))))
    return models


def _style_axis(ax):
    ax.set_facecolor(BG)
    ax.yaxis.grid(True, linestyle="--", color="#E5E7EB", alpha=0.7, zorder=0)
    ax.set_axisbelow(True)
    ax.xaxis.grid(False)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#E5E7EB")
    ax.spines["bottom"].set_color("#9CA3AF")


def chart_encoding_confound(models):
    """ASR vs Utility for the encoding defense, per model."""
    metrics = ["Naive ASR", "Utility"]
    x = np.arange(len(metrics))
    n = len(models)
    width = 0.8 / n

    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
    fig.patch.set_facecolor(BG)

    for i, (label, data) in enumerate(models):
        asr = data.get("naive", {}).get("encoding", {}).get("asr")
        util = data.get("utility", {}).get("encoding", {}).get("utility_rate")
        if util is None:  # older files may store utility under asr key
            util = data.get("utility", {}).get("encoding", {}).get("asr")
        vals = [
            (asr * 100) if asr is not None else 0,
            (util * 100) if util is not None else 0,
        ]
        offset = (i - (n - 1) / 2) * width
        bars = ax.bar(x + offset, vals, width=width, color=MODEL_COLORS[i % len(MODEL_COLORS)],
                      edgecolor="white", linewidth=0.5, zorder=3, label=label)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                    f"{val:.0f}%", ha="center", va="bottom",
                    fontsize=12, fontweight="bold", color="#1a1a2e")

    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=12, color="#374151")
    ax.set_ylim(0, 105)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_yticklabels([f"{v}%" for v in [0, 20, 40, 60, 80, 100]], fontsize=11, color="#6B7280")
    ax.set_ylabel("Rate", fontsize=12, color="#374151", labelpad=10)
    _style_axis(ax)
    ax.legend(frameon=False, fontsize=11, loc="upper left")

    fig.suptitle("Encoding Defense: ASR Is Only Meaningful Alongside Utility",
                 fontsize=16, fontweight="bold", color="#1a1a2e", x=0.05, ha="left", y=0.98)
    fig.text(0.05, 0.92,
             "Low ASR with near-zero utility is a broken pipeline, not a defense. "
             "Utility recovers as the model can decode base64.",
             fontsize=10, color="#6B7280", ha="left")
    plt.tight_layout(rect=[0, 0, 1, 0.88])
    out = "chart_compare_encoding.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"Saved {out}")


def chart_naive_asr_by_model(models):
    """Naive ASR for every defense, grouped by model."""
    defenses = [d for d in DEFENSE_ORDER
                if any(d in m[1].get("naive", {}) for m in models)]
    x = np.arange(len(defenses))
    n = len(models)
    width = 0.8 / n

    fig, ax = plt.subplots(figsize=(11, 6), dpi=150)
    fig.patch.set_facecolor(BG)

    for i, (label, data) in enumerate(models):
        naive = data.get("naive", {})
        vals = [(naive.get(d, {}).get("asr", 0) or 0) * 100 for d in defenses]
        offset = (i - (n - 1) / 2) * width
        bars = ax.bar(x + offset, vals, width=width, color=MODEL_COLORS[i % len(MODEL_COLORS)],
                      edgecolor="white", linewidth=0.5, zorder=3, label=label)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                    f"{val:.0f}", ha="center", va="bottom",
                    fontsize=10, fontweight="bold", color="#1a1a2e")

    ax.set_xticks(x)
    ax.set_xticklabels([DEFENSE_LABEL[d] for d in defenses], fontsize=11, color="#374151")
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_yticklabels([f"{v}%" for v in [0, 20, 40, 60, 80, 100]], fontsize=11, color="#6B7280")
    ax.set_ylabel("Attack Success Rate", fontsize=12, color="#374151", labelpad=10)
    _style_axis(ax)
    ax.legend(frameon=False, fontsize=11, loc="upper right")

    fig.suptitle("Naive Attack Success Rate by Defense and Model",
                 fontsize=16, fontweight="bold", color="#1a1a2e", x=0.05, ha="left", y=0.98)
    fig.text(0.05, 0.92, "Lower is better.", fontsize=10, color="#6B7280", ha="left")
    plt.tight_layout(rect=[0, 0, 1, 0.88])
    out = "chart_compare_naive_asr.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"Saved {out}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    models = parse_models(sys.argv[1:])
    chart_encoding_confound(models)
    chart_naive_asr_by_model(models)
