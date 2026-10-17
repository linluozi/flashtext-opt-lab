# -*- coding: utf-8 -*-
"""Benchmark: upstream vs optimised exact-match extraction.

Method
------
* Same process, A/B interleaved on every round (round 1: A,B; round 2: B,A; ...)
  so that allocator/GC drift hits both sides equally.
* Reported number is the **median of the per-round ratio**, not the ratio of
  medians -- the latter lets a single slow round dominate.
* Each configuration is measured in a fresh subprocess so that the keyword sets
  never share interpreter state.
* ``--no-write`` skips writing results.json (used by the smoke CI job).

Usage
-----
    python bench/benchmark.py                 # full run, writes bench/results.json
    python bench/benchmark.py --smoke         # tiny run, no results.json
    python bench/benchmark.py --no-write
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

BASELINE = os.path.join(ROOT, "baseline_pkg")
OPTIMISED = os.path.join(ROOT, "opt_pkg")


def _load(cls, path):
    keywords = [line.strip() for line in open(path, encoding="utf-8") if line.strip()]
    proc = cls()
    for kw in keywords:
        proc.add_keyword(kw)
    return proc


def _time_once(fn):
    start = time.perf_counter()
    fn()
    return time.perf_counter() - start


def measure(baseline_cls, optimised_cls, kw_path, doc_path, rounds, span_info):
    base = _load(baseline_cls, kw_path)
    opt = _load(optimised_cls, kw_path)
    doc = open(doc_path, encoding="utf-8").read()

    # warm up both sides so the first timed round is not a cold-start artefact
    for _ in range(2):
        base.extract_keywords(doc, span_info=span_info)
        opt.extract_keywords(doc, span_info=span_info)

    ratios, base_times, opt_times = [], [], []
    for r in range(rounds):
        if r % 2 == 0:
            tb = _time_once(lambda: base.extract_keywords(doc, span_info=span_info))
            to = _time_once(lambda: opt.extract_keywords(doc, span_info=span_info))
        else:
            to = _time_once(lambda: opt.extract_keywords(doc, span_info=span_info))
            tb = _time_once(lambda: base.extract_keywords(doc, span_info=span_info))
        ratios.append(tb / to)
        base_times.append(tb)
        opt_times.append(to)

    return {
        "keywords": os.path.basename(kw_path),
        "doc": os.path.basename(doc_path),
        "chars": len(doc),
        "n_keywords": len(base),
        "span_info": span_info,
        "base_ms_median": statistics.median(base_times) * 1e3,
        "opt_ms_median": statistics.median(opt_times) * 1e3,
        "speedup_median": statistics.median(ratios),
        "speedup_p10": statistics.quantiles(ratios, n=10)[0] if len(ratios) >= 10 else min(ratios),
        "speedup_p90": statistics.quantiles(ratios, n=10)[-1] if len(ratios) >= 10 else max(ratios),
        "rounds": rounds,
    }


def _child(payload):
    """Run one configuration in this process and print the JSON result."""
    sys.path.insert(0, BASELINE)
    import importlib
    base_mod = importlib.import_module("flashtext.keyword")
    Baseline = base_mod.KeywordProcessor
    del sys.modules["flashtext"]
    del sys.modules["flashtext.keyword"]
    sys.path.remove(BASELINE)
    sys.path.insert(0, OPTIMISED)
    opt_mod = importlib.import_module("flashtext.keyword")
    Optimised = opt_mod.KeywordProcessor
    result = measure(
        Baseline, Optimised,
        payload["kw_path"], payload["doc_path"], payload["rounds"], payload["span_info"],
    )
    print("RESULT " + json.dumps(result, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--rounds", type=int, default=15)
    ap.add_argument("--child", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--payload", default="", help=argparse.SUPPRESS)
    args = ap.parse_args()

    if args.child:
        _child(json.loads(args.payload))
        return

    if args.smoke:
        configs = [("kw_1k.txt", "doc_2000.txt"), ("kw_10k.txt", "doc_20000.txt")]
        rounds = 5
    else:
        configs = [
            (kw, doc)
            for kw in ("kw_1k.txt", "kw_10k.txt", "kw_48k.txt")
            for doc in ("doc_200.txt", "doc_2000.txt", "doc_20000.txt", "doc_200000.txt")
        ]
        rounds = args.rounds

    results = []
    for kw, doc in configs:
        for span_info in (False, True):
            payload = json.dumps({
                "kw_path": os.path.join(DATA, kw),
                "doc_path": os.path.join(DATA, doc),
                "rounds": rounds,
                "span_info": span_info,
            })
            out = subprocess.run(
                [sys.executable, os.path.abspath(__file__), "--child", "--payload", payload],
                capture_output=True, text=True,
            )
            line = next((l for l in out.stdout.splitlines() if l.startswith("RESULT ")), None)
            if line is None:
                sys.stderr.write(out.stdout + out.stderr)
                raise SystemExit("child failed for %s / %s" % (kw, doc))
            results.append(json.loads(line[len("RESULT "):]))

    print("%-12s %-16s %9s %8s %9s %9s %9s %8s" % (
        "keywords", "doc", "chars", "span", "base ms", "opt ms", "speedup", "p10-p90"))
    for r in results:
        print("%-12s %-16s %9d %8s %9.3f %9.3f %8.2fx  %.2f-%.2f" % (
            r["keywords"], r["doc"], r["chars"], r["span_info"],
            r["base_ms_median"], r["opt_ms_median"], r["speedup_median"],
            r["speedup_p10"], r["speedup_p90"]))

    if not args.no_write and not args.smoke:
        path = os.path.join(HERE, "results.json")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"python": sys.version.split()[0], "results": results}, fh,
                      ensure_ascii=False, indent=2)
            fh.write("\n")
        print("\nwrote", path)


if __name__ == "__main__":
    main()
