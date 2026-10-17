import sys, re, time, statistics
sys.path.insert(0,"bench"); sys.path.insert(0,"baseline_pkg")
from proto_v6 import Fast, load
from flashtext import KeywordProcessor as Base
kws=[l.strip() for l in open("data/kw_48k.txt",encoding="utf-8") if l.strip()]
b=load(Base,kws,False); f=Fast(b)
s=open("data/doc_20000.txt",encoding="utf-8").read().lower()
# cost of gate lookups alone
def gate_only():
    toks=[(m.group(),m.start(),m.end()) for m in f.pat.finditer(s)]
    c=0
    st=f.starts
    for i,t in enumerate(toks):
        g=st.get(t[0])
        if g is not None and (not g or (i+1<len(toks) and toks[i+1][0] in g)):
            c+=1
    return c
def single_only():
    toks=[(m.group(),m.start(),m.end()) for m in f.pat.finditer(s)]
    g=f.single.get
    return [g(t[0]) for t in toks]
def tm(label,fn,n=11):
    for _ in range(2): fn()
    xs=[]
    for _ in range(n):
        t0=time.perf_counter(); fn(); xs.append(time.perf_counter()-t0)
    print("%-30s %7.3f ms"%(label,statistics.median(xs)*1e3))
tm("tokenize only", lambda: [(m.group(),m.start(),m.end()) for m in f.pat.finditer(s)])
tm("tokenize+single.get", single_only)
tm("tokenize+gate", gate_only)
tm("v6 full", lambda: f.scan(s,False))
tm("base", lambda: b.extract_keywords(s))
