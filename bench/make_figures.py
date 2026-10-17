#!/usr/bin/env python
"""Generate the figures in charts/ from bench/results.json + bench/minof.txt.

Rule followed here: plot *ratios*, never absolute milliseconds as the primary
axis. Absolute wall-clock drifts across cases inside one process, so a
millisecond axis produces shapes that are measurement artefacts.

Run with the interpreter that has matplotlib installed:
    python bench/make_figures.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RESULTS = json.loads((ROOT / "bench" / "results.json").read_text(encoding="utf-8"))
OUT = ROOT / "charts"
OUT.mkdir(exist_ok=True)

# Warm editorial palette: espresso brown / amber gold / terracotta.
INK = "#2b2119"
PAPER = "#faf6f0"
AMBER = "#c8892b"
TERRACOTTA = "#b4552f"
OLIVE = "#6b6b3a"
MUTED = "#8a7a68"

plt.rcParams.update({
    "figure.facecolor": PAPER,
    "axes.facecolor": PAPER,
    "savefig.facecolor": PAPER,
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "text.color": INK,
    "axes.labelcolor": INK,
    "axes.edgecolor": MUTED,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.grid": True,
    "grid.color": "#e2d8c9",
    "grid.linewidth": 0.8,
})


def parse_minof():
    rows = []
    for line in (ROOT / "bench" / "minof.txt").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(kw_\d+k\.txt)\s+(\d+)\s+(True|False)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)x", line.strip())
        if m:
            rows.append({
                "kw": m.group(1), "chars": int(m.group(2)),
                "span": m.group(3) == "True",
                "ratio": float(m.group(6)),
            })
    return rows


def fig_scaling(rows):
    """Speedup vs document size, one line per keyword set, span=False."""
    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    colours = {"kw_1k.txt": AMBER, "kw_10k.txt": TERRACOTTA, "kw_48k.txt": OLIVE}
    labels = {"kw_1k.txt": "1.2k keywords", "kw_10k.txt": "10k keywords", "kw_48k.txt": "32k keywords"}
    offsets = {"kw_1k.txt": -13, "kw_10k.txt": 11, "kw_48k.txt": -13}
    for kw in ("kw_1k.txt", "kw_10k.txt", "kw_48k.txt"):
        pts = [r for r in rows if r["kw"] == kw and not r["span"]]
        pts.sort(key=lambda r: r["chars"])
        xs = [r["chars"] for r in pts]
        ys = [r["ratio"] for r in pts]
        ax.plot(xs, ys, "o-", color=colours[kw], linewidth=2.2, markersize=7,
                label=labels[kw], markeredgecolor=PAPER, markeredgewidth=1.2)
        for idx, (x, y) in enumerate(zip(xs, ys)):
            # only annotate the last point per line; label the rest sparsely to
            # avoid the right-hand pile-up seen in the first draft
            if idx in (0, len(xs) - 1):
                ax.annotate("%.2fx" % y, (x, y), textcoords="offset points",
                            xytext=(0, offsets[kw]), ha="center", fontsize=8, color=colours[kw])
    ax.set_xscale("log")
    ax.set_xlim(1200, 420000)
    ax.set_xlabel("document length (characters, log scale)")
    ax.set_ylabel("speedup  (upstream time / optimised time)")
    ax.set_title("Exact-match extraction speedup vs document size", color=INK,
                 fontsize=12, pad=12, loc="left")
    ax.set_ylim(1.0, 1.95)
    ax.axhline(1.0, color=MUTED, linewidth=1.0, linestyle=":")
    ax.annotate("no gain", (1300, 1.0), textcoords="offset points",
                xytext=(2, 4), fontsize=8, color=MUTED)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3, frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "speedup_vs_doc_size.png", dpi=160)
    plt.close(fig)


def fig_span(rows):
    """span_info on/off, grouped by keyword set at the largest document."""
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    kws = ("kw_1k.txt", "kw_10k.txt", "kw_48k.txt")
    labels = ("1.2k keywords", "10k keywords", "32k keywords")
    big = max(r["chars"] for r in rows)
    plain, span = [], []
    for kw in kws:
        p = [r["ratio"] for r in rows if r["kw"] == kw and not r["span"] and r["chars"] == big]
        s = [r["ratio"] for r in rows if r["kw"] == kw and r["span"] and r["chars"] == big]
        plain.append(p[0] if p else 0)
        span.append(s[0] if s else 0)
    x = range(len(kws))
    w = 0.36
    # bars are drawn from the 1.0 baseline, not from 0: starting at 0 would
    # visually inflate a 1.45x vs 1.63x difference into a ~10x-looking gap
    b1 = ax.bar([i - w / 2 for i in x], [v - 1 for v in plain], w, bottom=1,
                color=AMBER, label="span_info=False", edgecolor=PAPER, linewidth=1.2)
    b2 = ax.bar([i + w / 2 for i in x], [v - 1 for v in span], w, bottom=1,
                color=TERRACOTTA, label="span_info=True", edgecolor=PAPER, linewidth=1.2)
    for vals, bars in ((plain, b1), (span, b2)):
        for v, rect in zip(vals, bars):
            ax.annotate("%.2fx" % v, (rect.get_x() + rect.get_width() / 2, v),
                        textcoords="offset points", xytext=(0, 5), ha="center",
                        fontsize=9, color=INK)
    ax.axhline(1.0, color=MUTED, linewidth=1.0)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("speedup (baseline = 1.0)")
    ax.set_ylim(1.0, 1.85)
    ax.set_title("span_info costs a little of the gain (%s-character document)"
                 % "{:,}".format(big), color=INK, fontsize=11.5, pad=12, loc="left")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "span_vs_nospan.png", dpi=160)
    plt.close(fig)


def fig_distribution():
    """Per-round ratio spread from results.json (p10..p90 whiskers)."""
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    order = {"kw_1k.txt": 0, "kw_10k.txt": 1, "kw_48k.txt": 2}
    data = [r for r in RESULTS["results"] if r["span_info"] is False]
    data.sort(key=lambda r: (order[r["keywords"]], r["chars"]))
    labels = ["%s\n%s" % (r["keywords"].replace("kw_", "").replace(".txt", ""),
                          "{:,}".format(r["chars"])) for r in data]
    ys = [r["speedup_median"] for r in data]
    lo = [r["speedup_median"] - r["speedup_p10"] for r in data]
    hi = [r["speedup_p90"] - r["speedup_median"] for r in data]
    x = range(len(data))
    ax.errorbar(x, ys, yerr=[lo, hi], fmt="o", color=TERRACOTTA, ecolor=AMBER,
                elinewidth=2.0, capsize=4, markersize=6, markeredgecolor=PAPER)
    ax.axhline(1.0, color=MUTED, linewidth=1.0, linestyle=":")
    # group separators between keyword sets
    for boundary in (3.5, 7.5):
        ax.axvline(boundary, color=MUTED, linewidth=0.9, linestyle="--", alpha=0.6)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=7.8)
    ax.set_ylabel("speedup (median, p10-p90 whiskers)")
    ax.set_ylim(0.6, 2.4)
    ax.set_title("Per-round spread: median with p10-p90  (span_info=False)",
                 color=INK, fontsize=11.5, pad=12, loc="left")
    fig.tight_layout()
    fig.savefig(OUT / "spread_p10_p90.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    rows = parse_minof()
    fig_scaling(rows)
    fig_span(rows)
    fig_distribution()
    for p in sorted(OUT.glob("*.png")):
        print(p.name, p.stat().st_size, "bytes")
