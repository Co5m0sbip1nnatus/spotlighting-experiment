"""
Chart 2: Adaptive Attack ASR grouped by target defense.
Reads experiment results from JSON.

Usage:
    python chart2.py path/to/results.json
"""
import json
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Load results
results_path = sys.argv[1] if len(sys.argv) > 1 else "results.json"
with open(results_path) as f:
    data = json.load(f)

naive = data["naive"]
adaptive = data["adaptive"]

# Defense display config
DEFENSE_DISPLAY = {
    "delimiter": ("Delimiter", "#F59E0B"),
    "datamarking": ("Datamarking", "#6366F1"),
    "encoding": ("Encoding", "#10B981"),
}

# Attack name display config (snake_case -> human readable)
ATTACK_DISPLAY = {
    "delimiter_aware": "Delimiter-aware",
    "datamark_mimicking": "Datamark-mimicking",
    "pseudo_decoded": "Pseudo-decoded",
    "nested_base64": "Nested base64",
    "social_engineering": "Social engineering",
    "context_stuffing": "Context stuffing",
}

# Build groups from adaptive results
# adaptive keys look like "attack_name → defense_name"
groups = []
for defense_key, (defense_label, color) in DEFENSE_DISPLAY.items():
    attacks_for_defense = []
    # Naive baseline first
    if defense_key in naive:
        attacks_for_defense.append(("Naive baseline", naive[defense_key]["asr"] * 100, True))
    # Then adaptive attacks targeting this defense
    for adaptive_key, adaptive_data in adaptive.items():
        attack_name, _, target_defense = adaptive_key.partition(" \u2192 ")
        target_defense = target_defense.strip()
        if target_defense == defense_key:
            display_name = ATTACK_DISPLAY.get(attack_name.strip(), attack_name)
            attacks_for_defense.append((display_name, adaptive_data["asr"] * 100, False))
    groups.append((defense_label, color, attacks_for_defense))

# Compute x positions
positions, labels, heights, colors, is_baselines = [], [], [], [], []
group_centers, group_spans = [], []

x = 0
gap_within = 0.15
gap_between = 1.0

for defense_name, color, attacks in groups:
    group_start = x
    for attack_name, asr, is_baseline in attacks:
        positions.append(x)
        labels.append(attack_name)
        heights.append(asr)
        colors.append(color)
        is_baselines.append(is_baseline)
        x += 1 + gap_within
    group_end = x - gap_within - 1
    group_centers.append((group_start + group_end) / 2)
    group_spans.append((group_start - 0.4, group_end + 0.4))
    x += gap_between

# Figure
fig, ax = plt.subplots(figsize=(14, 7), dpi=150)
fig.patch.set_facecolor("#FAFBFC")
ax.set_facecolor("#FAFBFC")

# Bars
for pos, h, c, baseline in zip(positions, heights, colors, is_baselines):
    if baseline:
        ax.bar(pos, h, color=c, alpha=0.4, width=0.8,
               edgecolor=c, linewidth=2, linestyle="--", zorder=3)
    else:
        ax.bar(pos, h, color=c, alpha=0.95, width=0.8,
               edgecolor="white", linewidth=0.5, zorder=3)

# Value labels
for pos, h in zip(positions, heights):
    ax.text(pos, h + 1.5, f"{h:.0f}%",
            ha="center", va="bottom",
            fontsize=11, fontweight="bold", color="#1a1a2e")

# X labels (rotated)
ax.set_xticks(positions)
ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=10, color="#4B5563")

# Group labels
for (defense_name, color, _), center, (span_start, span_end) in zip(
    groups, group_centers, group_spans
):
    ax.text(center, 85, defense_name,
            ha="center", va="bottom",
            fontsize=13, fontweight="bold", color=color)
    ax.plot([span_start, span_end], [82, 82],
            color=color, linewidth=2, alpha=0.5, zorder=2)

# Y-axis
ax.set_ylim(0, 92)
ax.set_yticks([0, 20, 40, 60, 80])
ax.set_yticklabels(["0%", "20%", "40%", "60%", "80%"], fontsize=11, color="#6B7280")
ax.set_ylabel("Attack Success Rate", fontsize=12, color="#374151", labelpad=10)

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
    Patch(facecolor="#9CA3AF", alpha=0.4, edgecolor="#9CA3AF",
          linewidth=2, linestyle="--", label="Naive baseline"),
    Patch(facecolor="#9CA3AF", alpha=0.95, edgecolor="white",
          label="Adaptive attack"),
]
ax.legend(handles=legend_elements, loc="center right",
          fontsize=10, frameon=True, framealpha=0.9, edgecolor="#E5E7EB")

# Title
n_sample = next(iter(adaptive.values()))["total"]
fig.suptitle("Adaptive Attack Resilience by Defense",
             fontsize=16, fontweight="bold", color="#1a1a2e",
             x=0.05, ha="left", y=0.98)
fig.text(0.05, 0.94,
         f"How each defense holds up against attacks designed to bypass it. n={n_sample} per attack.",
         fontsize=10, color="#6B7280", ha="left")

plt.tight_layout(rect=[0, 0, 1, 0.91])
plt.savefig("chart2_adaptive_asr.png", dpi=150, bbox_inches="tight", facecolor="#FAFBFC")
plt.close()
print(f"Chart 2 saved (n={n_sample} per attack)")