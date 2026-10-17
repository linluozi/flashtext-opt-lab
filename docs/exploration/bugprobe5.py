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
sa = {(t,s,e) for t,s,e in a}; sb = {(t,s,e) for t,s,e in b}
miss = sorted(sa-sb, key=lambda x:x[1])
print("lost:", len(miss))
for t,s,e in miss[:6]:
    print("  hit=%r span=(%d,%d)" % (t,s,e))
    print("    ctx=%r" % doc[max(0,s-70):e+40])
