import sys, time, statistics
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as Base
kp=Base()
for l in open("data/kw_10k.txt",encoding="utf-8"):
    w=l.strip()
    if w: kp.add_keyword(w)
base=open("data/doc_20000.txt",encoding="utf-8").read()
def tm(fn,doc,n=5):
    fn(doc)
    xs=[]
    for _ in range(n):
        t0=time.perf_counter(); fn(doc); xs.append(time.perf_counter()-t0)
    return statistics.median(xs)
print("%-10s %10s %10s %10s %10s" % ("n","cost0 ms","ns/char","cost1 ms","ns/char"))
prev=None
for n in (5000,10000,20000,40000,80000,160000):
    doc=(base*10)[:n]
    t0=tm(lambda d: kp.extract_keywords(d,max_cost=0),doc)
    t1=tm(lambda d: kp.extract_keywords(d,max_cost=1),doc)
    print("%-10d %10.2f %10.1f %10.2f %10.1f" % (n,t0*1e3,t0/n*1e9,t1*1e3,t1/n*1e9))
