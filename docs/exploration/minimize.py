import sys
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor
kp = KeywordProcessor()
for line in open("data/kw_10k.txt", encoding="utf-8"):
    w=line.strip()
    if w: kp.add_keyword(w)
doc = open("data/doc_20000.txt", encoding="utf-8").read()

def lost(s):
    a=[(t,e) for t,_,e in kp.extract_keywords(s,max_cost=0,span_info=True)]
    b=[(t,e) for t,_,e in kp.extract_keywords(s,max_cost=1,span_info=True)]
    return len(set(a)-set(b))

seg = doc[400:560]
print("window lost count:", lost(seg), repr(seg[:80]))
# shrink from left
s = seg
changed=True
while changed:
    changed=False
    for cut in (1,2,4,8,16):
        while len(s)>cut and lost(s[cut:])>0:
            s=s[cut:]; changed=True
print("after left-shrink lost:", lost(s))
print(repr(s))
# shrink from right
changed=True
while changed:
    changed=False
    for cut in (1,2,4,8,16):
        while len(s)>cut and lost(s[:-cut])>0:
            s=s[:-cut]; changed=True
print("minimal:", repr(s), "lost:", lost(s))
print("  cost0:", kp.extract_keywords(s, max_cost=0))
print("  cost1:", kp.extract_keywords(s, max_cost=1))
