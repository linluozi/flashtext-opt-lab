import sys
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor

kp = KeywordProcessor(case_sensitive=True)
kp.add_keyword("the", "THE")
kp.add_keyword("not", "NOT")
print("plain      :", kp.extract_keywords("the cat is not here", max_cost=0))
print("max_cost=1 :", kp.extract_keywords("the cat is not here", max_cost=1))
print("max_cost=2 :", kp.extract_keywords("the cat is not here", max_cost=2))
print()
print("minimal: single exact keyword, one unrelated longer word present")
kp2 = KeywordProcessor(case_sensitive=True)
kp2.add_keyword("the", "THE")
for s in ["the", "the cat", "cats the", "a cats the dog", "the cats", "cats and the"]:
    print("  %-18r cost0=%-8s cost1=%s" % (s, kp2.extract_keywords(s, max_cost=0), kp2.extract_keywords(s, max_cost=1)))
