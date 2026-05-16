"""
Chart 3: Surprising finding - on Datamarking, defense-agnostic attacks
are more effective than defense-targeted attacks.

Reads experiment results from JSON.

Usage:
    python chart3.py path/to/results.json
"""
import json
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, FancyArrowPatch

# Load results
results_path = sys.argv[1] if len(sys.argv) > 1 else "results.json"
with open(results_path) as f:
    data = json.load(f)

naive = data["naive"]
adaptive = data["adaptive"]

# Extract ASR values targeting datamarking
def get_adaptive_asr(attack_name, defense="datamarking"):
    key = f"{attack_name} \u2192 {defense}"
    return adaptive[key]["asr"] * 100

# Build chart data (ordered for the visual story)
chart_data = [
    {
        "label": "Datamark-mimicking",
        "value": get_adaptive_asr("datamark_mimicking"),
        "category": "targeted",
        "desc": "Mimics the\ndefense pattern",
    },
    {
        "label": "Naive (baseline)",
        "value": naive["datamarking"]["asr"] * 100,
        "category": "baseline",
        "desc": "Generic injection\npayload",
    },
    {
        "label": "Social engineering",
        "value": get_adaptive_asr("social_engineering"),
        "category": "agnostic",
        "desc": "Disguised as\nlegitimate request",
    },
    {
        "label": "Context stuffing",
        "value": get_adaptive_asr("context_stuffing"),
        "category": "agnostic",
        "desc": "Pushes attack\nfar from\nsystem prompt",
    },
]

color_map = {
    "targeted": "#06B6D4",
    "baseline": "#9CA3AF",
    "agnostic": "#EF4444",
}

attacks = [d["label"] for d in chart_data]
asr_values = [d["value"] for d in chart_data]
colors = [color_map[d["category"]] for d in chart_data]
descriptions = [d["desc"] for d in chart_data]

# Figure
fig, ax = plt.subplots(figsize=(11, 7), dpi=150)
fig.patch.set_facecolor("#FAFBFC")
ax.set_facecolor("#FAFBFC")

# Bars
bars = ax.bar(attacks, asr_values, color=colors, alpha=0.92,
              width=0.6, edgecolor="white", linewidth=0.5, zorder=3)

# Value labels
for bar, val in zip(bars, asr_values):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{val:.0f}%",
            ha="center", va="bottom",
            fontsize=15, fontweight="bold", color="#1a1a2e")

# Sub-descriptions
for i, desc in enumerate(descriptions):
    ax.annotate(desc,
                xy=(i, 0), xycoords=("data", "data"),
                xytext=(0, -55), textcoords="offset points",
                ha="center", va="top",
                fontsize=10, color="#6B7280", linespacing=1.3)

# Annotation arrow: baseline -> highest agnostic
baseline_idx = next(i for i, d in enumerate(chart_data) if d["category"] == "baseline")
highest_agnostic_idx = max(
    (i for i, d in enumerate(chart_data) if d["category"] == "agnostic"),
    key=lambda i: chart_data[i]["value"]
)
arrow = FancyArrowPatch(
    (baseline_idx, asr_values[baseline_idx] + 1),
    (highest_agnostic_idx, asr_values[highest_agnostic_idx] + 1),
    connectionstyle="arc3,rad=-0.3",
    arrowstyle="->,head_width=0.4,head_length=0.6",
    color="#EF4444", linewidth=2, linestyle="--",
)
ax.add_patch(arrow)

# Annotation text
ax.text(2, 38,
        "Defense-agnostic attacks\nbypass datamarking BETTER\nthan targeted attacks",
        ha="center", va="bottom",
        fontsize=11, fontweight="600", color="#EF4444",
        linespacing=1.4)

# Y-axis
ax.set_ylim(0, 45)
ax.set_yticks([0, 10, 20, 30, 40])
ax.set_yticklabels(["0%", "10%", "20%", "30%", "40%"], fontsize=11, color="#6B7280")
ax.set_ylabel("Attack Success Rate", fontsize=12, color="#374151", labelpad=10)

ax.tick_params(axis="x", labelsize=12, colors="#1a1a2e", pad=8)

# Grid
ax.yaxis.grid(True, linestyle="--", color="#E5E7EB", alpha=0.7, zorder=0)
ax.set_axisbelow(True)
ax.xaxis.grid(False)

# Spines
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
ax.spines["left"].set_color("#E5E7EB")
ax.spines["bottom"].set_color("#9CA3AF")

# Legend
legend_elements = [
    Patch(facecolor=color_map["targeted"], alpha=0.92, label="Defense-targeted attack"),
    Patch(facecolor=color_map["baseline"], alpha=0.92, label="Naive baseline"),
    Patch(facecolor=color_map["agnostic"], alpha=0.92, label="Defense-agnostic attack"),
]
ax.legend(handles=legend_elements, loc="upper left",
          fontsize=10, frameon=True, framealpha=0.9, edgecolor="#E5E7EB")

# Title
n_sample = naive["datamarking"]["total"]
fig.suptitle("Surprising Finding: Datamarking is Weaker Against Generic Attacks",
             fontsize=16, fontweight="bold", color="#1a1a2e",
             x=0.05, ha="left", y=0.98)
fig.text(0.05, 0.93,
         f"Attacks that mimic the datamarking pattern are LESS effective than attacks that ignore it. n={n_sample} per attack.",
         fontsize=10, color="#6B7280", ha="left")

plt.tight_layout(rect=[0, 0.08, 1, 0.91])
plt.savefig("chart3_finding.png", dpi=150, bbox_inches="tight", facecolor="#FAFBFC")
plt.close()
print(f"Chart 3 saved (n={n_sample})")