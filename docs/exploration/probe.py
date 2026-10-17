import sys, time, cProfile, pstats, io
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor

def load(kwfile):
    kp = KeywordProcessor()
    for line in open(kwfile, encoding="utf-8"):
        w = line.strip()
        if w: kp.add_keyword(w)
    return kp

kp = load("data/kw_10k.txt")
doc = open("data/doc_20000.txt", encoding="utf-8").read()

# warm
for _ in range(3): kp.extract_keywords(doc)

t0 = time.perf_counter()
n = 20
for _ in range(n):
    r = kp.extract_keywords(doc)
dt = (time.perf_counter() - t0) / n
print("len(kp)", len(kp), "hits", len(r))
print("extract_keywords: %.3f ms/doc (%d chars)" % (dt*1e3, len(doc)))
print("throughput: %.2f MB/s" % (len(doc)/dt/1e6))

pr = cProfile.Profile(); pr.enable()
for _ in range(10): kp.extract_keywords(doc)
pr.disable()
s = io.StringIO(); pstats.Stats(pr, stream=s).sort_stats("tottime").print_stats(12)
print(s.getvalue())
