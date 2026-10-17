import sys
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor

print("=== budget decay: same typo repeated N times in one document ===")
kp = KeywordProcessor(case_sensitive=True)
kp.add_keyword("Marie", "Mary")
for n in (1,2,3,5,10):
    doc = " ".join(["Maria"]*n)
    got1 = kp.extract_keywords(doc, max_cost=1)
    got2 = kp.extract_keywords(doc, max_cost=2)
    print("  n=%-2d max_cost=1 -> %d/%d   max_cost=2 -> %d/%d" % (n, len(got1), n, len(got2), n))

print()
print("=== is it prefix-sensitive? (same typo, junk before it) ===")
for junk in (0,1,2,3,4,5):
    doc = " ".join(["qwertyuiop"]*junk + ["Maria"])
    print("  junk=%-2d -> %s" % (junk, kp.extract_keywords(doc, max_cost=1)))

print()
print("=== reset? fresh call vs accumulated state ===")
doc = " ".join(["Maria"]*6)
print("  first call :", len(kp.extract_keywords(doc, max_cost=1)), "/6")
print("  second call:", len(kp.extract_keywords(doc, max_cost=1)), "/6")
