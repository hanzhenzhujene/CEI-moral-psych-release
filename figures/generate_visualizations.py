#!/usr/bin/env python3
"""Generate benchmark result visualizations for the CEI Moral Psychology project."""

import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent.parent
RELEASE = ROOT / "results" / "release" / "2026-04-19-option1"
TROLLEY = ROOT / "results" / "trolleybench" / "20260421_100038"
OUT = ROOT / "figures" / "generated"
OUT.mkdir(parents=True, exist_ok=True)

# -- Style --
sns.set_theme(style="whitegrid", font_scale=1.1)
FAMILY_COLORS = {
    "Qwen": "#2dd4bf",
    "DeepSeek": "#60a5fa",
    "Llama": "#f97316",
    "Gemma": "#a78bfa",
    "MiniMax": "#f472b6",
}
SIZE_ORDER = ["S", "M", "L"]


# ============================================================
# 1. Benchmark Accuracy by Model Family (grouped bar chart)
# ============================================================
def plot_benchmark_accuracy():
    df = pd.read_csv(RELEASE / "faithful-metrics.csv")
    df = df[df["accuracy"].notna()].copy()

    # Pivot for grouped bar
    pivot = df.pivot_table(index="benchmark", columns="model_family", values="accuracy")
    pivot = pivot.reindex(columns=[c for c in ["Qwen", "DeepSeek", "Llama", "Gemma", "MiniMax"] if c in pivot.columns])

    fig, ax = plt.subplots(figsize=(12, 6))
    pivot.plot(kind="bar", ax=ax, color=[FAMILY_COLORS.get(c, "#999") for c in pivot.columns],
               edgecolor="white", width=0.7)
    ax.set_ylabel("Accuracy")
    ax.set_title("Benchmark Accuracy by Model Family (Option 1 Release)")
    ax.set_xlabel("")
    ax.set_ylim(0, 1)
    ax.legend(title="Model Family", loc="upper right")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    fig.savefig(OUT / "benchmark_accuracy_by_family.png", dpi=150)
    plt.close()
    print("  -> benchmark_accuracy_by_family.png")


# ============================================================
# 2. Scaling Curves (S → M → L per family per benchmark)
# ============================================================
def plot_scaling_curves():
    scaling = pd.read_csv(RELEASE / "family-scaling-summary.csv")

    records = []
    for _, row in scaling.iterrows():
        family = row["family"]
        for pair in row["numeric_pattern"].split("; "):
            parts = pair.split(": ")
            if len(parts) != 2:
                continue
            bench = parts[0].strip()
            for token in parts[1].split(" -> "):
                token = token.strip()
                if " " in token:
                    size_label, val = token.rsplit(" ", 1)
                else:
                    val = token
                    size_label = "L"
                try:
                    records.append({
                        "family": family,
                        "benchmark": bench,
                        "size": size_label,
                        "accuracy": float(val),
                    })
                except ValueError:
                    continue

    df = pd.DataFrame(records)
    benchmarks = df["benchmark"].unique()

    fig, axes = plt.subplots(1, len(benchmarks), figsize=(5 * len(benchmarks), 5), sharey=True)
    if len(benchmarks) == 1:
        axes = [axes]

    for ax, bench in zip(axes, benchmarks):
        sub = df[df["benchmark"] == bench]
        for family in sub["family"].unique():
            fsub = sub[sub["family"] == family].copy()
            # Order by size
            size_map = {"S": 0, "M": 1, "L": 2}
            fsub["size_idx"] = fsub["size"].map(size_map)
            fsub = fsub.sort_values("size_idx")
            ax.plot(fsub["size"], fsub["accuracy"], "o-",
                    color=FAMILY_COLORS.get(family, "#999"),
                    label=family, linewidth=2, markersize=8)
        ax.set_title(bench, fontweight="bold")
        ax.set_xlabel("Model Size")
        ax.set_ylim(0, 1)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
        ax.legend(fontsize=9)

    axes[0].set_ylabel("Accuracy")
    fig.suptitle("Scaling Curves: Accuracy by Model Size", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(OUT / "scaling_curves.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  -> scaling_curves.png")


# ============================================================
# 3. Coverage Heatmap (family × benchmark completion)
# ============================================================
def plot_coverage_heatmap():
    df = pd.read_csv(RELEASE / "family-size-progress.csv")

    # Build matrix: rows = family-size, cols = benchmarks
    benchmarks = ["unimoral", "smid", "value_kaleidoscope", "ccd_bench", "denevil", "moralbench", "emnlp_educator"]
    bench_labels = ["UniMoral", "SMID", "Value\nKaleidoscope", "CCD-Bench", "Denevil", "MoralBench", "EMNLP\nEducator"]
    status_map = {"done": 1.0, "live": 0.6, "queue": 0.3, "tbd": 0.1, "proxy": 0.8, "partial": 0.5, "error": 0.15, "-": 0.0}

    rows = []
    for _, row in df.iterrows():
        label = row["line_label"]
        vals = []
        for b in benchmarks:
            s = str(row.get(b, "tbd")).strip()
            vals.append(status_map.get(s, 0.0))
        rows.append({"line": label, **{bl: v for bl, v in zip(bench_labels, vals)}})

    matrix = pd.DataFrame(rows).set_index("line")

    fig, ax = plt.subplots(figsize=(14, 8))
    cmap = sns.color_palette("YlGnBu", as_cmap=True)
    sns.heatmap(matrix, annot=False, cmap=cmap, linewidths=1, linecolor="white",
                ax=ax, vmin=0, vmax=1, cbar_kws={"label": "Completion"})

    # Add text annotations with original status
    for i, (_, row) in enumerate(df.iterrows()):
        for j, b in enumerate(benchmarks):
            s = str(row.get(b, "tbd")).strip()
            color = "white" if status_map.get(s, 0) > 0.5 else "black"
            ax.text(j + 0.5, i + 0.5, s, ha="center", va="center",
                    fontsize=9, color=color, fontweight="bold")

    ax.set_title("Benchmark Coverage Matrix (Family × Size)", fontweight="bold", fontsize=13)
    ax.set_ylabel("")
    ax.set_xlabel("")
    plt.tight_layout()
    fig.savefig(OUT / "coverage_heatmap.png", dpi=150)
    plt.close()
    print("  -> coverage_heatmap.png")


# ============================================================
# 4. Trolley Problem: Ethical Consistency Index (ECI)
# ============================================================
def plot_trolley_eci():
    with open(TROLLEY / "eval_summary.json") as f:
        data = json.load(f)

    records = []
    for key, val in data.items():
        parts = key.split("_T")
        family_size = parts[0]
        temp = f"T={parts[1]}"
        family, size = family_size.rsplit("-", 1)
        records.append({
            "family": family.capitalize(),
            "size": size,
            "temp": temp,
            "eci": val["eci"]["eci"],
            "reversal_rate": val["followup_impact"]["reversal_rate"],
            "mean_inconsistency": val["entropy_inconsistency"]["mean_inconsistency"],
        })

    df = pd.DataFrame(records)

    # ECI grouped by family
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Panel 1: ECI
    for family in df["family"].unique():
        fsub = df[df["family"] == family]
        for temp in ["T=0.0", "T=0.7"]:
            tsub = fsub[fsub["temp"] == temp].copy()
            size_map = {"S": 0, "M": 1, "L": 2}
            tsub["size_idx"] = tsub["size"].map(size_map)
            tsub = tsub.sort_values("size_idx")
            ls = "-" if temp == "T=0.0" else "--"
            axes[0].plot(tsub["size"], tsub["eci"], f"o{ls}",
                         color=FAMILY_COLORS.get(family, "#999"),
                         label=f"{family} {temp}", linewidth=2, markersize=7)

    axes[0].set_title("Ethical Consistency Index (ECI)", fontweight="bold")
    axes[0].set_xlabel("Model Size")
    axes[0].set_ylabel("ECI (higher = more consistent)")
    axes[0].set_ylim(0, 1)
    axes[0].legend(fontsize=7, ncol=2)

    # Panel 2: Reversal Rate
    for family in df["family"].unique():
        fsub = df[df["family"] == family]
        for temp in ["T=0.0", "T=0.7"]:
            tsub = fsub[fsub["temp"] == temp].copy()
            size_map = {"S": 0, "M": 1, "L": 2}
            tsub["size_idx"] = tsub["size"].map(size_map)
            tsub = tsub.sort_values("size_idx")
            ls = "-" if temp == "T=0.0" else "--"
            axes[1].plot(tsub["size"], tsub["reversal_rate"], f"o{ls}",
                         color=FAMILY_COLORS.get(family, "#999"),
                         label=f"{family} {temp}", linewidth=2, markersize=7)

    axes[1].set_title("Follow-up Reversal Rate", fontweight="bold")
    axes[1].set_xlabel("Model Size")
    axes[1].set_ylabel("Reversal Rate (lower = more stable)")
    axes[1].set_ylim(0, 1)
    axes[1].legend(fontsize=7, ncol=2)

    fig.suptitle("Trolley Problem: Moral Reasoning Consistency", fontsize=14, fontweight="bold")
    plt.tight_layout()
    fig.savefig(OUT / "trolley_consistency.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  -> trolley_consistency.png")


# ============================================================
# 5. Trolley Problem: Framework Distribution
# ============================================================
def plot_trolley_frameworks():
    with open(TROLLEY / "eval_summary.json") as f:
        data = json.load(f)

    records = []
    for key, val in data.items():
        parts = key.split("_T")
        family_size = parts[0]
        temp = f"T={parts[1]}"
        family, size = family_size.rsplit("-", 1)
        fd = val["framework_distribution"]
        total = sum(fd.values())
        for framework, count in fd.items():
            records.append({
                "model": f"{family.capitalize()}-{size} ({temp})",
                "family": family.capitalize(),
                "framework": framework.capitalize(),
                "fraction": count / total if total > 0 else 0,
            })

    df = pd.DataFrame(records)
    pivot = df.pivot_table(index="model", columns="framework", values="fraction", fill_value=0)

    fig, ax = plt.subplots(figsize=(12, 8))
    pivot.plot(kind="barh", stacked=True, ax=ax,
               color=["#2dd4bf", "#f97316", "#a78bfa", "#94a3b8"],
               edgecolor="white")
    ax.set_xlabel("Proportion of Responses")
    ax.set_title("Trolley Problem: Ethical Framework Distribution by Model", fontweight="bold")
    ax.legend(title="Framework", loc="lower right")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
    plt.tight_layout()
    fig.savefig(OUT / "trolley_frameworks.png", dpi=150)
    plt.close()
    print("  -> trolley_frameworks.png")


# ============================================================
# 6. Sample Count Summary
# ============================================================
def plot_sample_counts():
    df = pd.read_csv(RELEASE / "benchmark-summary.csv")

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(df["benchmark"], df["samples"], color="#2dd4bf", edgecolor="white")
    for bar, val in zip(bars, df["samples"]):
        ax.text(bar.get_width() + 500, bar.get_y() + bar.get_height() / 2,
                f"{val:,}", va="center", fontsize=10)
    ax.set_xlabel("Total Samples Evaluated")
    ax.set_title("Evaluation Scale by Benchmark", fontweight="bold")
    ax.invert_yaxis()
    plt.tight_layout()
    fig.savefig(OUT / "sample_counts.png", dpi=150)
    plt.close()
    print("  -> sample_counts.png")


# ============================================================
if __name__ == "__main__":
    print("Generating CEI Benchmark Visualizations...")
    print()
    plot_benchmark_accuracy()
    plot_scaling_curves()
    plot_coverage_heatmap()
    plot_trolley_eci()
    plot_trolley_frameworks()
    plot_sample_counts()
    print()
    print(f"All figures saved to {OUT}/")
