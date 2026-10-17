# -*- coding: utf-8 -*-
"""Differential test: the optimised exact-match fast path must be byte-identical
to the upstream character-by-character trie loop.

The baseline is a frozen copy of the upstream implementation
(``tests/upstream_reference.py``), so this test keeps working even after the
optimised code changes.

Run:
    python -m pytest tests -q
"""
import os
import random
import string
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "opt_pkg"))
sys.path.insert(0, HERE)

from flashtext import KeywordProcessor as Optimised  # noqa: E402
from upstream_reference import KeywordProcessor as Reference  # noqa: E402


def _pair(keywords, case_sensitive=False, update=None):
    opt = Optimised(case_sensitive=case_sensitive)
    ref = Reference(case_sensitive=case_sensitive)
    for kw in keywords:
        clean = (update or {}).get(kw)
        opt.add_keyword(kw, clean)
        ref.add_keyword(kw, clean)
    return opt, ref


def _compare(testcase, keywords, sentences, case_sensitive=False, update=None):
    opt, ref = _pair(keywords, case_sensitive, update)
    for sentence in sentences:
        for span_info in (False, True):
            got = opt.extract_keywords(sentence, span_info=span_info)
            want = ref.extract_keywords(sentence, span_info=span_info)
            testcase.assertEqual(
                got, want,
                "mismatch for %r (keywords=%r, span_info=%r, case_sensitive=%r)"
                % (sentence, keywords[:8], span_info, case_sensitive),
            )


class TestExactFastPathEquivalence(unittest.TestCase):
    def test_handwritten_cases(self):
        cases = [
            (["the"], ["the cat", "the", "there", "a the b", "THE cat"]),
            (["cat"], ["cat", "cats", "cat9", "cat_9", " cat ", "concat"]),
            (["new", "new york"], ["new york city", "new yorker", "new", "new, york"]),
            (["new york"], ["new york", "new  york", "new\nyork", "new-york", "new.york"]),
            (["a"], ["a", "a a a", "aa", "b a b"]),
            (["abc", "bcd"], ["abcd", "abc bcd", "zabcdz"]),
            (["Marie", "Mariah"], ["Marias", "Maria", "marie", "MARIAH"]),
            ([".NET", "NET"], [".NET framework", "NET", "a .NET b"]),
            (["te-", "is--"], ["te-", "te", "is--", "is"]),
            (["x"], ["", "   ", "\n\n", "x", "x x"]),
            (["very long keyword phrase here"],
             ["very long keyword phrase here", "very long keyword phrase hereby"]),
            (["Ab"], ["ab", "AB", "aB", "Ab"]),
        ]
        for keywords, sentences in cases:
            for case_sensitive in (False, True):
                _compare(self, keywords, sentences, case_sensitive)

    def test_span_boundaries(self):
        keywords = ["new", "new york", "york", "or"]
        sentences = ["new york", "new yorker", "a new york b", "new-york", "new york."]
        for case_sensitive in (False, True):
            _compare(self, keywords, sentences, case_sensitive)

    def test_update_clean_names(self):
        keywords = ["alpha", "beta", "alpha beta"]
        update = {"alpha": "A", "beta": "B", "alpha beta": "AB"}
        sentences = ["alpha beta", "alpha", "beta gamma", "alpha beta gamma"]
        _compare(self, keywords, sentences, update=update)

    def test_after_removal_index_is_rebuilt(self):
        """Adding then removing keywords must not leave a stale index behind."""
        opt, ref = _pair(["XBP1", "XBP1s", "UPR", "UPRs"])
        for proc in (opt, ref):
            proc.remove_keyword("XBP1")
            proc.remove_keyword("UPRs")
        sentence = "XBP1s is UPR"
        self.assertEqual(opt.extract_keywords(sentence), ref.extract_keywords(sentence))
        self.assertEqual(opt.extract_keywords(sentence), ["XBP1s", "UPR"])

    def test_mutation_after_index_is_built(self):
        """The index must be invalidated by mutations made *after* a first call.

        This is the case that a naive "add everything, then extract" test misses:
        here the fast-path index is materialised first, and only then does the
        keyword set change.
        """
        opt, ref = _pair(["alpha", "alphabet"], case_sensitive=True)
        # build the index on both sides
        self.assertEqual(opt.extract_keywords("alphabet"), ref.extract_keywords("alphabet"))
        self.assertEqual(opt.extract_keywords("alphabet"), ["alphabet"])

        for proc in (opt, ref):
            proc.remove_keyword("alphabet")
        # upstream never reports a strict prefix at end-of-string; the optimised
        # path must reproduce that quirk exactly
        self.assertEqual(opt.extract_keywords("alphabet"), ref.extract_keywords("alphabet"))
        self.assertEqual(opt.extract_keywords("alphabet"), [])

        for proc in (opt, ref):
            proc.add_keyword("alphabet", "ALPHABET")
        self.assertEqual(opt.extract_keywords("alphabet"), ref.extract_keywords("alphabet"))
        self.assertEqual(opt.extract_keywords("alphabet"), ["ALPHABET"])

        # same for a whole-document call, which is what a stale index breaks
        for proc in (opt, ref):
            proc.remove_keyword("alphabet")
        self.assertEqual(opt.extract_keywords("an alphabet book"), ref.extract_keywords("an alphabet book"))
        # "alphabet" is one token, so "alpha" is not reported inside it
        self.assertEqual(opt.extract_keywords("an alphabet book"), [])
        self.assertEqual(opt.extract_keywords("an alpha book"), ["alpha"])

    def test_longest_phrase_wins_among_shared_prefixes(self):
        """Two phrases sharing the same (tok0, tok1) pair: the longest must win.

        Without this case, sorting the candidate bucket the wrong way round
        (shortest first) still passes every other test.
        """
        keywords = ["a b", "a b c d", "a b c"]
        sentences = ["a b c d", "a b c", "a b", "a b c d e"]
        for case_sensitive in (True, False):
            _compare(self, keywords, sentences, case_sensitive)
        opt, _ = _pair(keywords, case_sensitive=True)
        self.assertEqual(opt.extract_keywords("a b c d"), ["a b c d"])
        self.assertEqual(opt.extract_keywords("a b c"), ["a b c"])

    def test_prefix_never_matches_inside_a_longer_word(self):
        """Upstream does not report a keyword that is a strict prefix of a token."""
        opt, ref = _pair(["cat", "alpha"], case_sensitive=True)
        for sentence in ["cats", "cat9", "cat_9", "alphabet", "cat", "alpha"]:
            self.assertEqual(
                opt.extract_keywords(sentence), ref.extract_keywords(sentence),
                "prefix handling differs for %r" % sentence,
            )

    def test_non_word_boundary_changes_invalidate_index(self):
        opt, ref = _pair(["a-b"], case_sensitive=True)
        self.assertEqual(opt.extract_keywords("a-b"), ref.extract_keywords("a-b"))
        for proc in (opt, ref):
            proc.add_non_word_boundary("-")
        # now '-' is a word character, so "a-b" is one token and the keyword
        # "a-b" must be found as a whole
        self.assertEqual(opt.extract_keywords("a-b"), ref.extract_keywords("a-b"))

    def test_fuzzy_path_untouched(self):
        """max_cost > 0 must go through the original loop (unchanged output)."""
        keywords = ["Marie", "Bay Area", "Big Apple"]
        sentences = ["Maria", "Big Aple", "Baay Area", "Marie Blanc"]
        for case_sensitive in (False, True):
            for max_cost in (1, 2):
                opt, ref = _pair(keywords, case_sensitive)
                for sentence in sentences:
                    for span_info in (False, True):
                        self.assertEqual(
                            opt.extract_keywords(sentence, span_info=span_info, max_cost=max_cost),
                            ref.extract_keywords(sentence, span_info=span_info, max_cost=max_cost),
                        )


class TestExactFastPathFuzz(unittest.TestCase):
    """Randomised differential test over adversarial alphabets."""

    def _random_case(self, rnd):
        # tiny alphabets force overlaps, prefix chains and separator mixes
        alphabet = rnd.choice([
            "ab",
            "abc",
            "aA_9",
            "ab .-_",
            "abAB09_ .\n-",
        ])
        def word(lo=1, hi=6):
            return "".join(rnd.choice(alphabet) for _ in range(rnd.randint(lo, hi)))
        keywords = []
        for _ in range(rnd.randint(1, 12)):
            kw = word()
            if kw.strip() and kw not in keywords:
                keywords.append(kw)
        sentences = [word(1, 24) for _ in range(rnd.randint(1, 6))]
        return keywords, sentences

    def test_fuzz(self):
        rnd = random.Random(20261017)
        for _ in range(400):
            keywords, sentences = self._random_case(rnd)
            for case_sensitive in (False, True):
                _compare(self, keywords, sentences, case_sensitive)


class TestReferenceCopyIntegrity(unittest.TestCase):
    """The differential test is only meaningful if the reference really is upstream.

    This guard exists because the first version of the suite compared the two
    files in *text* mode, which silently normalises CRLF: the reference copy had
    been written with CRLF line endings (34,213 bytes vs upstream's 33,406) and
    the comparison still reported "identical". Comparing raw bytes is the only
    check that cannot be fooled that way.
    """

    def test_reference_is_byte_identical_to_upstream(self):
        upstream = os.path.join(ROOT, "upstream", "keyword.py")
        reference = os.path.join(HERE, "upstream_reference.py")
        with open(upstream, "rb") as fh:
            a = fh.read()
        with open(reference, "rb") as fh:
            b = fh.read()
        self.assertEqual(len(a), 33406, "upstream keyword.py size changed")
        self.assertNotIn(b"\r\n", b, "reference copy has CRLF line endings")
        self.assertEqual(a, b, "tests/upstream_reference.py drifted from upstream")


if __name__ == "__main__":
    unittest.main()
