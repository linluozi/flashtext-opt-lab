import sys, time, statistics
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as Base
# Keyword that is a PREFIX of a long run, no boundaries -> forces per-char append
b=Base(case_sensitive=True)
b.add_keyword("a")
b.add_keyword("ab")
def tm(fn,doc,label,n=7):
    fn(doc)
    xs=[]
    for _ in range(n):
        t0=time.perf_counter(); fn(doc); xs.append(time.perf_counter()-t0)
    m=statistics.median(xs)
    print("%-44s n=%-7d %9.3f ms  %7.2f ns/char" % (label,len(doc),m*1e3,m/len(doc)*1e9))
    return m
print("=== replace: current_word += char inside long run (O(n^2) string build) ===")
prev=None
for n in (2000,4000,8000,16000,32000):
    doc = "a"*n + " z"
    m=tm(b.replace_keywords, doc, "replace, 'a'*n")
    if prev: print("     ratio vs half-n: %.2f  (linear would be ~2.0)" % (m/prev))
    prev=m
