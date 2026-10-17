import sys, re, time, statistics
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as Base
s=open("data/doc_20000.txt",encoding="utf-8").read().lower()
N=len(s)
def tm(label,fn,n=13):
    for _ in range(2): fn()
    xs=[]
    for _ in range(n):
        t0=time.perf_counter(); fn(); xs.append(time.perf_counter()-t0)
    m=statistics.median(xs)
    print("%-42s %8.3f ms  %6.1f ns/char"%(label,m*1e3,m/N*1e9))
    return m

print("=== upstream cost decomposed ===")
for kwf in ("kw_1k.txt","kw_48k.txt"):
    b=Base(); [b.add_keyword(l.strip()) for l in open("data/"+kwf,encoding="utf-8") if l.strip()]
    tm(kwf+" full extract", lambda: b.extract_keywords(s))
    tm(kwf+" full extract (lower already)", lambda: b.extract_keywords(s))
print()
print("=== absolute floors ===")
tm("doc.lower()", lambda: s.lower())
import re
TOK=re.compile(r"[0-9A-Za-z_]+")
tm("findall tokens", lambda: TOK.findall(s))
tm("finditer tokens", lambda: [m.group() for m in TOK.finditer(s)])
