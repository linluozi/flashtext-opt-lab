import sys, time
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor

def load(f):
    kp = KeywordProcessor()
    for line in open(f, encoding="utf-8"):
        w = line.strip()
        if w: kp.add_keyword(w)
    return kp

doc = open("data/doc_20000.txt", encoding="utf-8").read()
for kwf in ("kw_1k.txt","kw_10k.txt","kw_48k.txt"):
    kp = load("data/"+kwf)
    for mc in (0,1,2):
        for _ in range(2): kp.extract_keywords(doc, max_cost=mc)
        t0=time.perf_counter(); n=5
        for _ in range(n): r=kp.extract_keywords(doc, max_cost=mc)
        dt=(time.perf_counter()-t0)/n
        print("%-12s kw=%-6d max_cost=%d  %.2f ms  hits=%d" % (kwf, len(kp), mc, dt*1e3, len(r)))
