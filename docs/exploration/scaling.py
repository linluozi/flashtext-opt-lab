import sys, time
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor

def t(kp, doc, **kw):
    best=1e9
    for _ in range(3):
        t0=time.perf_counter(); kp.extract_keywords(doc, **kw); best=min(best,time.perf_counter()-t0)
    return best

print("=== scaling with document length, fixed keyword set ===")
kp = KeywordProcessor()
for line in open("data/kw_10k.txt", encoding="utf-8"):
    w=line.strip()
    if w: kp.add_keyword(w)
for n in (2000, 5000, 10000, 20000, 40000, 80000):
    doc = (open("data/doc_20000.txt", encoding="utf-8").read()*5)[:n]
    dt=t(kp,doc)
    print("  n=%-7d %.2f ms  %.3f us/char" % (n, dt*1e3, dt/n*1e6))

print()
print("=== pathological: long phrase keyword + text of its prefix repeated ===")
for K in (5, 10, 20, 40):
    kp2 = KeywordProcessor()
    kw = " ".join(["a"]*K) + " z"
    kp2.add_keyword(kw)
    for N in (200, 400, 800, 1600):
        doc = " ".join(["a"]*N) + " y"
        dt=t(kp2,doc)
        print("  K=%-3d N=%-5d %.3f ms   %.4f us/char" % (K, N, dt*1e3, dt/len(doc)*1e6))
    print()
