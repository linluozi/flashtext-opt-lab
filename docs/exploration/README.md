# Exploration scripts (archive)

These are the throwaway probes used while looking for the optimisation, kept for
traceability. They are **not** part of the deliverable and are not wired into the
test suite.

Several of them were written while `data/` and the prototype modules still sat in
the repository root, so their relative paths no longer resolve. Running them from
`docs/exploration/` will fail with `FileNotFoundError`; run them from the repo
root after copying, or just read them.

What each group established:

| Script | Question it answered |
|---|---|
| `bugprobe*.py` | Whether the fuzzy path has behavioural defects. It does (`max_cost=1` drops exact hits; the per-keyword edit budget leaks across phrases). Those two are already covered by upstream issues #150 and #148, so they were deliberately **not** touched here. |
| `floor.py`, `breakdown.py`, `micro*.py` | How fast a pure C-level tokenisation + dict lookup is: ~30 ns/char vs upstream's ~170 ns/char. This is what justified the whole direction. |
| `proto*.py`, `v9.py`, `v10.py` | Successive fast-path designs. v1–v8 either regressed on large keyword sets or broke equivalence; v10 (token dict + `(tok0, tok1)` gate + `startswith`) is the one that became `opt_pkg`. |
| `gate*.py`, `plist.py` | Why a first-token-only gate is not enough: with 32k keywords a single token such as `the` can start up to 535 phrase candidates. |
| `dbg*.py` | Step-through traces for the equivalence bugs (candidate recording timing, single-character first tokens, the `is--` tails bucket). |
| `fuzzy_*.py` | Measurements of the fuzzy path, used to decide *not* to optimise it. |
| `e2e_rep.py`, `final_attr.py` | Repeat-run and attribution checks behind the numbers quoted in the report. |
