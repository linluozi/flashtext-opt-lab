import sys
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor

print("=== D: does the fuzzy match depend on keyword INSERTION ORDER? ===")
for order in (("Marie","Mariah"), ("Mariah","Marie")):
    kp = KeywordProcessor(case_sensitive=True)
    for k in order: kp.add_keyword(k, "CLEAN:"+k)
    print("  insert order %-22s -> %s" % (order, kp.extract_keywords("Marias", max_cost=1)))

print()
print("=== E: does it pick the MINIMUM cost match? ===")
# 'Mario' is distance 1 from 'Maria', 'Marias' is distance 1 too; 'Mari' distance 2
kp = KeywordProcessor(case_sensitive=True)
kp.add_keyword("Marianne")   # dist 3 from "Mario"? let's just observe
kp.add_keyword("Mario")      # dist 1
print("  'Mario' vs [Marianne(d3), Mario(d1)] ->", kp.extract_keywords("Mario", max_cost=2))

print()
print("=== F: why does max_cost=2 find FEWER than max_cost=1? ===")
kp2 = KeywordProcessor(case_sensitive=True)
kp2.add_keyword("Marie", "Mary")
for mc in (0,1,2,3):
    print("  'Maria' max_cost=%d -> %s" % (mc, kp2.extract_keywords("Maria", max_cost=mc)))
