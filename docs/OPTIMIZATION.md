# flashtext exact-match fast path — optimisation report

Upstream project: **vi3k6i5/flashtext** 2.7 (MIT)
Upstream commit used: `master` @ `2025-04-13` (`codeload` tarball, `keyword.py` sha1
`79ea1f84065a9ea2a38d564c4dd734d5c03dd5a3`, 807 lines)

---

## 1. Verified facts about the upstream project

| Item | Value | How verified |
|---|---|---|
| Repository | https://github.com/vi3k6i5/flashtext | `GET /repos/vi3k6i5/flashtext` → `full_name` |
| Stars / open issues | 5,705 / 74 | same API response |
| Archived | `false` | same API response |
| Last push | 2025-04-13 | same API response |
| Licence | **MIT** (`Copyright (c) 2017 Vikash Singh`) | `LICENSE` in the tarball + GitHub `license.spdx_id` |
| PyPI | `flashtext` 2.7 | `GET https://pypi.org/pypi/flashtext/json` |
| Source obtained | `https://codeload.github.com/vi3k6i5/flashtext/tar.gz/refs/heads/master` | downloaded, 99,577 bytes |
| Test suite | 39 tests, all green on the untouched tree | `pytest test -q` → `39 passed` |

Nothing in this report comes from a search snippet: the API metadata, the licence
file, the source and the test run were all inspected directly.

---

## 2. What the original algorithm does, and where it hurts

`KeywordProcessor.extract_keywords()` walks a character trie **one character at a
time in Python**:

```python
while idx < sentence_len:
    char = sentence[idx]
    if char not in self.non_word_boundaries:      # word boundary
        ...
    elif char in current_dict:                    # advance trie
        current_dict = current_dict[char]
    else:                                         # miss -> skip to end of word
        idy = idx + 1
        while idy < sentence_len:
            char = sentence[idy]
            if char not in self.non_word_boundaries:
                break
            idy += 1
        idx = idy
```

Every character of the document costs at least one loop iteration, one set
membership test and one dict membership test — even when the character cannot
possibly start a keyword. The consequence is a flat per-character cost that is
independent of how many keywords are actually present:

| Workload | Upstream throughput |
|---|---|
| 20,000-char real prose, 10k keywords | 3.4 ms → **170 ns/char** |
| 200,000-char real prose, 10k keywords | 35 ms → **175 ns/char** |

A pure C-level tokenisation of the same text plus one dict lookup per token
measures **30 ns/char** (`re.findall` + `dict.get`). So the character loop is
about **5x slower than the work actually required** by the exact-match case.

Two structural facts make the fast path possible (both derived from the code and
then verified differentially, see §4):

1. A candidate can only *start* at the first character of a word run (the loop
   only advances the trie while `char in current_dict`, and skips the rest of the
   run on a miss).
2. A candidate is only *accepted* when the next character is a word boundary (or
   at end-of-string), i.e. exactly at the end of a run.

So for `max_cost == 0` the answer is fully determined by the maximal
`[0-9A-Za-z_]+` runs of the document plus the keyword set.

---

## 3. The optimisation

`extract_keywords()` gains a fast path that is used **only when `max_cost <= 0`**.
The fuzzy path (`max_cost > 0`) is untouched.

### 3.1 Single-token keywords → one dict lookup per token

All keywords that contain no separator (`the`, `python`, `XBP1s`, …) go into a
plain `dict` keyed by the token. The document is split into runs with a single
compiled regex, so the per-character Python loop disappears entirely.

### 3.2 Multi-token keywords → `(token0, token1)` gate + `str.startswith`

Keywords such as `new york` need the *exact* separator characters — upstream
rejects `new  york`, `new-york` and `new\nyork`. They are therefore matched with
`str.startswith` on the full keyword string (C level), but only after a
two-token gate, so at most a handful of candidates is ever tried.

The gate matters: with 32k keywords, gating on the first token alone leaves up to
**535** candidates for a single token (`the`), which made an earlier version
*slower* than upstream. Gating on `(token0, token1)` cuts the worst bucket down
by roughly two orders of magnitude.

### 3.3 Correctness details that are easy to get wrong

| Trap | What upstream actually does | Handling |
|---|---|---|
| Keyword that is a strict prefix of a token | `cat` does **not** match `cats` | prefix probing is bounded to the run, so it never fires mid-token |
| Keyword ending in separators (`is--`, `te-`) | matches, and the trailing separators are consumed | kept in a separate `tails` bucket, consulted **in addition to** the phrase bucket |
| Keyword starting with a separator (`.NET`) | matches at a non-word char | not representable by run lookup → the whole fast path declines and the original loop runs |
| Case-insensitive mode | lower-cases the document first | the fast path lower-cases before scanning |
| Longest match wins | later hits overwrite earlier ones | candidate buckets are sorted longest-first |
| Trie mutated after the first call | n/a (no cache upstream) | the index is dropped on `add_keyword`, `remove_keyword`, `set_non_word_boundaries`, `add_non_word_boundary` |

The last row is not theoretical: a first draft cached the index but only
invalidated it in `add_keyword`, and `remove_keyword` silently returned stale
matches. The mutation test in §4 catches that (`M4`, `M9`).

### 3.4 Fallback, not breakage

`_build_exact_index()` returns `None` whenever the keyword set cannot be
represented (leading-separator keyword, no word characters at all). In that case
`extract_keywords()` falls through to the **unmodified** upstream loop, so
behaviour is preserved for every keyword set, only the speed differs.

### 3.5 Why the fuzzy path was deliberately left alone

While profiling, the fuzzy path (`max_cost > 0`) turned out to be **about 10x
slower** than the exact path (33.5 ms vs 3.2 ms on the same 20,000-char document,
10k keywords) and it also has two genuine behavioural defects:

* with `max_cost=1`, 213 exact matches that the exact path finds are **lost** on
  the 20,000-char document (`from the ` → only `from them` comes back);
* the per-keyword edit budget leaks across unrelated phrases, so an unsuccessful
  candidate earlier in the document consumes the budget of a later one.

Both are already reported upstream as open issues
[#150](https://github.com/vi3k6i5/flashtext/issues/150) ("Reset fuzzy edit budgets
after unsuccessful phrases") and
[#148](https://github.com/vi3k6i5/flashtext/issues/148) ("Match trailing
insertions within the fuzzy edit budget"), with open PRs attached. Re-fixing them
here would duplicate in-flight work and would change results rather than preserve
them, so this deliverable stays strictly orthogonal: **exact path faster, fuzzy
path untouched, outputs identical**. The probes that established the defects are
kept in `docs/exploration/bugprobe*.py`.

---

## 4. Verification

### 4.1 Differential test against a frozen upstream copy

`tests/upstream_reference.py` is a **byte-identical copy** of the upstream
`keyword.py` (verified by comparing the raw bytes: both are 33,406 bytes, LF
line endings, sha1 `79ea1f84065a9ea2a38d564c4dd734d5c03dd5a3`).
`tests/test_exact_fast_path.py` compares the two implementations on:

* 12 hand-written keyword/sentence groups × case-sensitive on/off × span_info on/off;
* span boundary cases;
* `update=` clean-name mapping;
* index invalidation after `add_keyword` / `remove_keyword` made **after** the
  index was already materialised;
* `add_non_word_boundary` changing the tokenisation;
* the fuzzy path (`max_cost` 1 and 2) — must be bit-identical too;
* **400 randomised fuzz rounds** over adversarial alphabets (`ab`, `aA_9`,
  `ab .-_`, `abAB09_ .\n-`) × case-sensitive on/off.

```
$ python -m pytest tests -q
..........                                                               [100%]
11 passed
```

### 4.2 Mutation testing — are those tests actually able to fail?

A green suite proves nothing on its own. Ten deliberate bugs were injected one at
a time into the optimised file; **all ten were caught**:

| # | Injected bug | Result |
|---|---|---|
| M1 | drop the end-of-string / boundary check | 1 failed |
| M2 | sort candidates shortest-first (breaks "longest wins") | 1 failed |
| M3 | skip lower-casing in case-insensitive mode | 3 failed |
| M4 | do not invalidate the index on `remove_keyword` | 1 failed |
| M5 | allow leading-separator keywords in the index | 2 failed |
| M6 | remove the second-token gate | 5 failed |
| M7 | do not skip tokens already consumed by a match | 2 failed |
| M8 | report the token end instead of the match end in spans | 5 failed |
| M9 | do not invalidate the index on `add_keyword` | 1 failed |
| M10 | drop the `tails` bucket | 2 failed |

The first run of this exercise caught only 8 of 10 — M2 and M4 survived. Both
were real coverage holes (no test used two phrases sharing a `(tok0, tok1)` pair;
no test mutated the keyword set after a first extraction). The suite was extended
until they failed too; the table above is the post-fix run.

### 4.3 Upstream test suite still green

```
$ PYTHONPATH=opt_pkg python -m pytest test -q
39 passed
```

### 4.4 Whole-book end-to-end check

Three complete Project Gutenberg novels (0.58M–1.24M characters) were extracted
with both implementations and the results compared element by element — this is
what found the `is--` bug in §3.3 that the synthetic fuzz alphabet missed.

| Book | chars | hits | identical? | speedup (7 interleaved rounds) |
|---|---|---|---|---|
| `en1342.txt` (Pride and Prejudice) | 732,275 | 91,137 | yes | 1.60–1.63x |
| `en1661.txt` (Sherlock Holmes) | 581,601 | 73,736 | yes | 1.55–1.75x |
| `en2701.txt` (Moby Dick) | 1,238,312 | 153,527 | yes | 1.53–1.65x |
| `en98.txt` (Tale of Two Cities) | 776,912 | 98,468 | yes | 1.59–1.60x |

Ranges, not single points: repeated runs of `bench/e2e.py` moved each book by a
few percent (e.g. Sherlock Holmes 1.54x → 1.75x → 1.55x), so the honest claim is
"around 1.5–1.7x on million-character real text", not a precise multiplier.

---

## 5. Performance results

### 5.1 Method

* Same process, **A/B interleaved every round** (round 1: A,B; round 2: B,A; …),
  so allocator and GC drift hits both sides equally.
* Reported figure is the **median of the per-round ratios**, not the ratio of
  medians — the latter lets one slow round dominate.
* Each configuration runs in a **fresh subprocess** so keyword sets never share
  interpreter state.
* `bench/minof.py` additionally reports **min-of-25**, which is the most stable
  statistic when a single gen-2 GC pause lands inside one of the samples.

### 5.2 min-of-25 speedup (most conservative stable read)

```
kw           doc       span   base min    opt min min ratio
kw_1k.txt    2000     False      0.259      0.166     1.56x
kw_1k.txt    20000    False      2.586      1.660     1.56x
kw_1k.txt    200000   False     28.229     17.338     1.63x
kw_10k.txt   2000     False      0.276      0.167     1.65x
kw_10k.txt   20000    False      3.658      2.110     1.73x
kw_10k.txt   200000   False     35.987     21.514     1.67x
kw_48k.txt   2000     False      0.251      0.170     1.48x
kw_48k.txt   20000    False      3.281      2.437     1.35x
kw_48k.txt   200000   False     35.934     24.725     1.45x
```

With `span_info=True` the gain narrows to **1.25x–1.55x**, because building the
`(value, start, end)` tuples is work both implementations must do.

![speedup vs document size](../charts/speedup_vs_doc_size.png)

![span_info vs no span](../charts/span_vs_nospan.png)

### 5.3 Honest reading of the spread

![per-round spread](../charts/spread_p10_p90.png)

The p10–p90 whiskers are wide. Two things are worth stating plainly:

* On a **200-char document** the absolute times are 20 µs; the ratio is noisy and
  the wall-clock saving is negligible. The fast path is not aimed at that size.
* Some rounds dip **below 1.0x** (p10 = 0.72 in the worst 32k/20k case). That is a
  gen-2 GC pause landing inside the optimised sample: in one isolated run the
  optimised side showed `2.26 2.10 1.94 **22.53** 2.89 …` ms — a single 22 ms
  outlier among 1.9 ms samples. Filtering it out, the same configuration is
  1.35x. `min-of-N` and the interleaved median both agree on ~1.3–1.7x; only the
  raw p10 is dragged down by the pause.

No speedup figure in this report was extrapolated or estimated — every number
above comes from `bench/results.json`, `bench/minof.txt` or `bench/e2e.txt` in
this archive, which can be regenerated with the commands in §6.

---

## 6. Reproducing

```bash
# tests (10 differential + fuzz cases, plus a byte-integrity guard on the reference copy)
python -m pytest tests -q

# upstream's own 39 tests against the optimised package
PYTHONPATH=opt_pkg python -m pytest test -q

# full benchmark matrix (24 configurations, 25 interleaved rounds each)
python bench/benchmark.py --rounds 25

# min-of-25 table
python bench/minof.py

# whole-book end-to-end equivalence + timing
python bench/e2e.py

# regenerate the charts (needs matplotlib)
python bench/make_figures.py
```

---

## 7. Licence and attribution

The upstream code is MIT, `Copyright (c) 2017 Vikash Singh`. `LICENSE` is
included unchanged. Every modification is marked in the source with a
`MODIFIED (optimisation)` comment and is confined to
`opt_pkg/flashtext/keyword.py`; the complete diff against upstream is
`docs/keyword.py.patch` (165 added lines, 1 changed line, no deletions of
upstream logic).

Files that are **not** modified: `flashtext/__init__.py`, `setup.py`, the test
suite in `test/`, and the upstream documentation.
