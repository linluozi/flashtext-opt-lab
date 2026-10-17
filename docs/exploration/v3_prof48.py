import sys, re, time, statistics, collections
sys.path.insert(0,"baseline_pkg")
sys.path.insert(0,"bench")
from proto_v3 import Fast, load
from flashtext import KeywordProcessor as Base
kws=[l.strip() for l in open("data/kw_48k.txt",encoding="utf-8") if l.strip()]
b=load(Base,kws,False); f=Fast(b)
doc=open("data/doc_20000.txt",encoding="utf-8").read()
low=doc.lower()
toks=[m.group() for m in f.pat.finditer(low)]
print("tokens",len(toks))
print("single hits",sum(1 for t in toks if t in f.single))
print("starts hits",sum(1 for t in toks if t in f.starts))
print("trie walks triggered", sum(1 for i,t in enumerate(toks) if t in f.starts and (not f.starts[t] or (i+1<len(toks) and toks[i+1] in f.starts[t]))))
print("max keyword len", max(len(k) for k in b.get_all_keywords()))
print("distinct first tokens in starts", len(f.starts))
def tm(label,fn,n=11):
    for _ in range(2): fn()
    xs=[]
    for _ in range(n):
        t0=time.perf_counter(); fn(); xs.append(time.perf_counter()-t0)
    print("%-30s %7.3f ms"%(label,statistics.median(xs)*1e3))
tm("base", lambda: b.extract_keywords(doc))
tm("v3", lambda: f.scan(low))
tm("tokenize only", lambda: [m.group() for m in f.pat.finditer(low)])
