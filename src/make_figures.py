"""Deterministically create the three manuscript figures.

Figure 1 is a non-quantitative conceptual schematic. Figures 2 and 3 are
derived only from frozen structural result tables. No private data enter.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"


COLORS = {
    "sufficient": "#2C7FB8",
    "misleading": "#F28E2B",
    "ambiguous": "#59A14F",
    "ink": "#222222",
    "muted": "#6B7280",
    "panel": "#F5F7FA",
}


def configure() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "legend.fontsize": 9,
        "figure.dpi": 180,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    })


def box(ax, x, y, width, height, text, facecolor="white", fontsize=10) -> None:
    patch = FancyBboxPatch(
        (x - width / 2, y - height / 2), width, height,
        boxstyle="round,pad=0.02,rounding_size=0.05",
        facecolor=facecolor, edgecolor=COLORS["ink"], linewidth=1.2,
    )
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize)


def arrow(ax, start, end, color=None, style="-") -> None:
    ax.annotate(
        "", xy=end, xytext=start,
        arrowprops={"arrowstyle": "->", "lw": 1.5, "color": color or COLORS["ink"], "linestyle": style},
    )


def figure_1() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.2))
    for ax, title in zip(
        axes,
        ("A. Binary structural indicators", "B. Intervention-effect evidence"),
    ):
        ax.set_facecolor(COLORS["panel"])
        ax.set_title(title, loc="left", fontweight="bold")
        ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis("off")

    left, right = axes
    box(left, 1.2, 5.2, 1.1, 0.8, "I")
    box(left, 1.2, 1.8, 1.1, 0.8, "R")
    box(left, 4.3, 5.2, 1.4, 0.8, "M1")
    box(left, 4.3, 1.8, 1.4, 0.8, "M2")
    box(left, 8.5, 3.5, 1.1, 0.8, "Y")
    arrow(left, (1.75, 5.2), (3.6, 5.2), style="--")
    arrow(left, (1.75, 1.8), (3.6, 1.8), style="--")
    arrow(left, (5.0, 5.05), (7.95, 3.78), style="--")
    arrow(left, (5.0, 1.95), (7.95, 3.22), style="--")
    left.text(4.9, 6.0, "S(I,Y) = 1; S(R,Y) = 1", ha="center", color=COLORS["muted"])
    left.text(5.0, 0.65, "Both candidates reach Y; structural indicators\ndo not rank intervention effects.", ha="center")

    box(right, 1.5, 5.2, 1.2, 0.8, "I")
    box(right, 1.5, 1.8, 1.2, 0.8, "R")
    box(right, 5.2, 3.5, 3.1, 1.0, r"sign of $\tau(I,R\rightarrow Y)$", facecolor="white")
    box(right, 8.6, 3.5, 1.7, 1.0, "I or R", facecolor="#E8F1F8")
    arrow(right, (2.1, 5.1), (3.65, 3.8), color=COLORS["sufficient"])
    arrow(right, (2.1, 1.9), (3.65, 3.2), color=COLORS["sufficient"])
    arrow(right, (6.75, 3.5), (7.75, 3.5), color=COLORS["sufficient"])
    right.text(5.0, 0.65, "The same query is ranked using an\nintervention-specific contrast.", ha="center")

    fig.suptitle("Structural indicators versus intervention-effect evidence for a pairwise query", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "figure_1_structure_vs_effect.png", metadata={"Software": "matplotlib"})
    plt.close(fig)


def figure_2() -> None:
    direct = pd.read_csv(RESULTS / "structure_effect_decision_v1_query_level.csv")
    path = pd.read_csv(RESULTS / "structure_effect_path_robustness_v1_query_level.csv")
    conditions = [
        ("GT Direct", direct["gt_structure_state"]),
        ("GT Ancestry", path.loc[path.structural_source.eq("gt"), "path_state"]),
        ("Method D Direct", direct["method_d_state"]),
        ("Method D Ancestry", path.loc[path.structural_source.eq("method_d"), "path_state"]),
    ]
    states = ["STRUCTURE_SUFFICIENT", "STRUCTURE_MISLEADING", "STRUCTURE_AMBIGUOUS"]
    labels = ["Sufficient / oracle-consistent", "Misleading / oracle-discordant", "Ambiguous / abstain"]
    counts = np.array([[int(series.eq(state).sum()) for state in states] for _, series in conditions])
    fig, ax = plt.subplots(figsize=(10.4, 5.2))
    bottom = np.zeros(4)
    for index, label in enumerate(labels):
        bars = ax.bar(
            range(4), counts[:, index], bottom=bottom, label=label,
            color=(COLORS["sufficient"], COLORS["misleading"], COLORS["ambiguous"])[index],
            width=0.72,
        )
        for bar, value, base in zip(bars, counts[:, index], bottom):
            ax.text(bar.get_x() + bar.get_width() / 2, base + value / 2, str(value), ha="center", va="center")
        bottom += counts[:, index]
    ax.set_title("Decision-state composition under structural-indicator policies", fontweight="bold")
    ax.set_ylabel("Queries (n = 50 per condition)")
    ax.set_xticks(range(4), [name for name, _ in conditions], rotation=6)
    ax.set_ylim(0, 54)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure_2_decision_states.png", metadata={"Software": "matplotlib"})
    plt.close(fig)


def figure_3() -> None:
    transitions = pd.read_csv(RESULTS / "draft2_reviewer_structural_transitions_v1.csv")
    transitions = transitions.loc[transitions.record_type.eq("transition")]
    states = ["SUFFICIENT", "MISLEADING", "AMBIGUOUS"]
    labels = ["Sufficient", "Misleading", "Ambiguous"]
    fig, axes = plt.subplots(1, 2, figsize=(9.3, 4.2), constrained_layout=True)
    for ax, source, title in zip(axes, ("GT", "METHOD_D"), ("GT structure", "Method D")):
        part = transitions.loc[transitions.structural_source.eq(source)]
        matrix = np.zeros((3, 3), dtype=int)
        for row in part.itertuples(index=False):
            matrix[states.index(row.direct_state), states.index(row.path_state)] = int(row.count)
        image = ax.imshow(matrix, cmap="Blues", vmin=0, vmax=matrix.max())
        threshold = matrix.max() / 2
        for i in range(3):
            for j in range(3):
                ax.text(j, i, str(matrix[i, j]), ha="center", va="center",
                        color="white" if matrix[i, j] > threshold else COLORS["ink"],
                        fontsize=13, fontweight="bold")
        ax.set_title(title, fontweight="bold")
        ax.set_xticks(range(3), labels, rotation=25, ha="right")
        ax.set_yticks(range(3), labels)
        ax.set_xlabel("Ancestry-policy state")
        ax.set_ylabel("Direct-edge-policy state")
        for spine in ax.spines.values():
            spine.set_visible(False)
    fig.suptitle("Direct-to-ancestry query-state transitions", fontweight="bold")
    fig.colorbar(image, ax=axes, shrink=0.78, label="Queries")
    fig.savefig(FIGURES / "figure_3_transition_matrices.png", metadata={"Software": "matplotlib"})
    plt.close(fig)


if __name__ == "__main__":
    configure()
    FIGURES.mkdir(exist_ok=True)
    figure_1()
    figure_2()
    figure_3()
