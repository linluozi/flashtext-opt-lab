import sys, time, statistics
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as Base
kws=[l.strip() for l in open("data/kw_10k.txt",encoding="utf-8") if l.strip()]
b=Base()
for k in kws: b.add_keyword(k)
def tm(fn,doc,label):
    fn(doc)
    xs=[]
    for _ in range(7):
        t0=time.perf_counter(); fn(doc); xs.append(time.perf_counter()-t0)
    m=statistics.median(xs)
    print("%-46s n=%-7d %9.3f ms  %7.1f ns/char" % (label,len(doc),m*1e3,m/len(doc)*1e9))

print("=== extract vs replace on same input ===")
for n in (2500, 5000, 10000, 20000, 40000):
    doc = ("中"*n)                      # single CJK run, no boundary chars
    tm(b.extract_keywords, doc, "extract, CJK run n=%d"%n)
    tm(b.replace_keywords, doc, "replace, CJK run n=%d"%n)
    print()
