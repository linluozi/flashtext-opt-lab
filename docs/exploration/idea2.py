import sys, re
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor
kp = KeywordProcessor()
for line in open("data/kw_10k.txt", encoding="utf-8"):
    w=line.strip()
    if w: kp.add_keyword(w)
doc = open("data/doc_20000.txt", encoding="utf-8").read()
ref = kp.extract_keywords(doc, span_info=True)
# find the reference hit that v1 missed, and inspect
allkw = kp.get_all_keywords()
print("kw 'gardiner'?", allkw.get("gardiner"))
print("kw 'meanwhile'?", allkw.get("meanwhile"))
print("kw 'mr'?", allkw.get("mr"))
i = doc.find("Gardiner, meanwhile")
print(repr(doc[i-30:i+40]))
# what did original return around there?
for t,s,e in ref:
    if 0 <= s-i+30 < 60 or abs(s-i)<40:
        print("  ", t, s, e, repr(doc[s:e]))
