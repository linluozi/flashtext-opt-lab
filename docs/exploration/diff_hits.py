import sys
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor
kp = KeywordProcessor()
for line in open("data/kw_10k.txt", encoding="utf-8"):
    w=line.strip()
    if w: kp.add_keyword(w)
doc = open("data/doc_20000.txt", encoding="utf-8").read()
a = kp.extract_keywords(doc, max_cost=0, span_info=True)
b = kp.extract_keywords(doc, max_cost=1, span_info=True)
c = kp.extract_keywords(doc, max_cost=2, span_info=True)
sa = {(t,s,e) for t,s,e in a}
sb = {(t,s,e) for t,s,e in b}
sc = {(t,s,e) for t,s,e in c}
print("exact hits", len(a), "fuzzy1", len(b), "fuzzy2", len(c))
print("in exact but NOT in fuzzy1:", len(sa-sb))
for x in list(sa-sb)[:5]: print("   ", x, repr(doc[x[1]-3:x[2]+3]))
print("in fuzzy2 but NOT in fuzzy1:", len(sc-sb))
for x in list(sc-sb)[:5]: print("   ", x)
print("in fuzzy1 but NOT in fuzzy2:", len(sb-sc))
for x in list(sb-sc)[:8]: print("   ", x, repr(doc[max(0,x[1]-5):x[2]+5]))
