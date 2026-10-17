# Benchmark data

All text is **public domain**, downloaded from Project Gutenberg.

## Documents

| file | chars | source |
|---|---|---|
| `en1342.txt` | 732,275 | *Pride and Prejudice* — https://www.gutenberg.org/cache/epub/1342/pg1342.txt |
| `en1661.txt` | 581,601 | *The Adventures of Sherlock Holmes* — https://www.gutenberg.org/cache/epub/1661/pg1661.txt |
| `en2701.txt` | 1,238,312 | *Moby Dick* — https://www.gutenberg.org/cache/epub/2701/pg2701.txt |
| `en98.txt` | 776,912 | *A Tale of Two Cities* — https://www.gutenberg.org/cache/epub/98/pg98.txt |
| `doc_200.txt` … `doc_200000.txt` | 200 / 1,997 / 19,998 / 199,991 | contiguous slices of the above, cut on a word boundary |

The Gutenberg header/footer is stripped before slicing.

## Keyword sets

`kw_1k.txt`, `kw_10k.txt`, `kw_48k.txt` are built from the **same four books** so
that the vocabulary and the documents come from the same register of English:

* single-token entries: the most frequent tokens of length >= 3 in those books;
* multi-token entries: the most frequent bigrams found in the same text.

Because the keywords are drawn from the corpus, hit rates are high (roughly 5–6%
of tokens match), which is the realistic case for entity extraction and is also
the case that stresses the candidate-gate the most.

Regenerate with `docs/exploration/make_data.py` (run from the repository root).
