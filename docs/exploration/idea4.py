import sys, re
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor
kp = KeywordProcessor()
for line in open("data/kw_10k.txt", encoding="utf-8"):
    w=line.strip()
    if w: kp.add_keyword(w)
doc = open("data/doc_20000.txt", encoding="utf-8").read()
allkw = kp.get_all_keywords()
TOK = re.compile(r"[0-9A-Za-z_]+")
def v1(s):
    s = s.lower()
    out=[]
    for m in TOK.finditer(s):
        t=m.group(); v=allkw.get(t)
        if v is not None: out.append((v,m.start(),m.end()))
        else:
            for L in range(len(t)-1,0,-1):
                v=allkw.get(t[:L])
                if v is not None: out.append((v,m.start(),m.start()+L)); break
    return out
ref = kp.extract_keywords(doc, span_info=True)
got = v1(doc)
sr={(a,b,c) for a,b,c in ref}; sg={(a,b,c) for a,b,c in got}
print("ref",len(ref),"got",len(got),"missing",len(sr-sg),"extra",len(sg-sr))
for x in sorted(sr-sg,key=lambda z:z[1])[:5]: print("  MISS", x, repr(doc[x[1]-25:x[2]+15]))
for x in sorted(sg-sr,key=lambda z:z[1])[:5]: print("  EXTRA", x, repr(doc[x[1]-25:x[2]+15]))
