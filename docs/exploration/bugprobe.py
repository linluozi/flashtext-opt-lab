import sys
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor

print("=== A: does fuzzy capability degrade across a document? ===")
kp = KeywordProcessor(case_sensitive=True)
kp.add_keyword("Marie", "Mary")
# one unrelated word that costs 1, then the real typo later
for prefix in ("", "zzzz ", "zzzz zzzz ", "zzzz zzzz zzzz "):
    s = prefix + "Maria"
    print("  prefix=%-16r -> %s" % (prefix, kp.extract_keywords(s, max_cost=1)))

print()
print("=== B: keyword ending at punctuation other than . , space ===")
for tail in [".", ",", " ", "!", "?", ";", ":", "-", "\"", ")" ]:
    s = "I met Maria" + tail + " yesterday"
    print("  tail=%-3r -> %s" % (tail, kp.extract_keywords(s, max_cost=1)))

print()
print("=== C: same word, position dependence (single doc, exact vs fuzzy) ===")
kp2 = KeywordProcessor(case_sensitive=True)
kp2.add_keyword("Marie", "Mary")
doc = "zzzz Marie zzzz Maria"
print("  exact:", kp2.extract_keywords(doc))
print("  fuzzy:", kp2.extract_keywords(doc, max_cost=1))
