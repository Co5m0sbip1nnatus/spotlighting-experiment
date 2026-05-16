"""
Chart 1: Naive Attack ASR across all defense methods.
Reads experiment results from JSON.

Usage:
    python chart1.py path/to/results.json
"""
import json
import sys
import matplotlib.pyplot as plt

# Load results
results_path = sys.argv[1] if len(sys.argv) > 1 else "results.json"
with open(results_path) as f:
    data = json.load(f)

naive_results = data["naive"]

# Display config: defense_name -> (display label, color)
DEFENSE_DISPLAY = {
    "no_defense": ("No Defense", "#DC2626"),
    "instructions_only": ("Instructions\nOnly", "#F59E0B"),
    "delimiter": ("Delimiter", "#F59E0B"),
    "datamarking": ("Datamarking", "#6366F1"),
    "encoding": ("Encoding", "#10B981"),
}

# Extract data in display order
defenses, asr_values, colors = [], [], []
for key, (label, color) in DEFENSE_DISPLAY.items():
    if key in naive_results:
        defenses.append(label)
        asr_values.append(naive_results[key]["asr"] * 100)
        colors.append(color)

# Figure setup
fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
fig.patch.set_facecolor("#FAFBFC")
ax.set_facecolor("#FAFBFC")

# Bars
bars = ax.bar(defenses, asr_values, color=colors, width=0.6,
              edgecolor="white", linewidth=0.5, zorder=3)

# Value labels
for bar, val in zip(bars, asr_values):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 2,
            f"{val:.0f}%",
            ha="center", va="bottom",
            fontsize=14, fontweight="bold", color="#1a1a2e")

# Y-axis
ax.set_ylim(0, 80)
ax.set_yticks([0, 20, 40, 60, 80])
ax.set_yticklabels(["0%", "20%", "40%", "60%", "80%"], fontsize=11, color="#6B7280")
ax.set_ylabel("Attack Success Rate", fontsize=12, color="#374151", labelpad=10)

# X-axis
ax.tick_params(axis="x", labelsize=11, colors="#374151", pad=8)

# Title (n is read from data)
n_per_defense = next(iter(naive_results.values()))["total"]
fig.suptitle("Naive Attack Success Rate by Defense Method",
             fontsize=16, fontweight="bold", color="#1a1a2e",
             x=0.05, ha="left", y=0.97)
fig.text(0.05, 0.92,
         f"Lower is better. n={n_per_defense} documents per defense. Llama 3.1 8B.",
         fontsize=10, color="#6B7280", ha="left")

# Grid
ax.yaxis.grid(True, linestyle="--", color="#E5E7EB", alpha=0.7, zorder=0)
ax.set_axisbelow(True)
ax.xaxis.grid(False)

# Spines
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
ax.spines["left"].set_color("#E5E7EB")
ax.spines["bottom"].set_color("#9CA3AF")

plt.tight_layout(rect=[0, 0, 1, 0.88])
plt.savefig("chart1_naive_asr.png", dpi=150, bbox_inches="tight", facecolor="#FAFBFC")
plt.close()
print(f"Chart 1 saved (n={n_per_defense} per defense)")