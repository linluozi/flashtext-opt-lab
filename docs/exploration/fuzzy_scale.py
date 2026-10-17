import sys, time, statistics
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as Base
def load(kwf):
    kp=Base()
    for l in open("data/"+kwf,encoding="utf-8"):
        w=l.strip()
        if w: kp.add_keyword(w)
    return kp
def tm(fn,doc,n=5):
    fn(doc)
    xs=[]
    for _ in range(n):
        t0=time.perf_counter(); fn(doc); xs.append(time.perf_counter()-t0)
    return statistics.median(xs)
doc=open("data/doc_20000.txt",encoding="utf-8").read()
print("%-12s %8s %10s %10s %10s" % ("kwset","#kw","cost0 ms","cost1 ms","cost2 ms"))
for kwf in ("kw_1k.txt","kw_10k.txt","kw_48k.txt"):
    kp=load(kwf)
    t0=tm(lambda d: kp.extract_keywords(d,max_cost=0),doc)
    t1=tm(lambda d: kp.extract_keywords(d,max_cost=1),doc)
    t2=tm(lambda d: kp.extract_keywords(d,max_cost=2),doc)
    print("%-12s %8d %10.2f %10.2f %10.2f" % (kwf,len(kp),t0*1e3,t1*1e3,t2*1e3))
print()
print("=== OOV density effect (cost=1) ===")
kp=load("kw_10k.txt")
import re
words=re.findall(r"[A-Za-z]+",doc)
oov=[w for w in words if w.lower() not in kp.get_all_keywords()]
print("tokens",len(words),"OOV",len(oov),"(%.0f%%)"%(100*len(oov)/len(words)))
for frac in (0,0.25,0.5,1.0):
    k=int(len(oov)*frac)
    d=" ".join(oov[:k]+words[:len(words)-k])
    print("  oov_frac=%.2f n=%d  cost1=%.2f ms" % (frac,len(d),tm(lambda x: kp.extract_keywords(x,max_cost=1),d)*1e3))
