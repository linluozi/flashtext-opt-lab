import sys, re, time, statistics
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as Base
doc = open("data/doc_20000.txt", encoding="utf-8").read()
N=len(doc)
kws=[l.strip() for l in open("data/kw_10k.txt",encoding="utf-8") if l.strip()]
b=Base()
for k in kws: b.add_keyword(k)
nwb=b.non_word_boundaries
cls=''.join(re.escape(c) for c in sorted(nwb))
pat=re.compile('['+cls+']+')
low=doc.lower()

def tm(label, fn, n=25):
    for _ in range(3): fn()
    xs=[]
    for _ in range(n):
        t0=time.perf_counter(); fn(); xs.append(time.perf_counter()-t0)
    print("%-44s %7.3f ms  %6.1f ns/char" % (label, statistics.median(xs)*1e3, statistics.median(xs)/N*1e9))

tm("base extract", lambda: b.extract_keywords(doc))
tm("doc.lower() only", lambda: doc.lower())
tm("finditer over lower (no body)", lambda: [m.start() for m in pat.finditer(low)])
tm("base extract (already lower input)", lambda: b.extract_keywords(low))
import re as _re
print("tokens:", len(pat.findall(low)))
