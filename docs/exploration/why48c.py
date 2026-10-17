import sys, re, time, statistics
sys.path.insert(0,"bench"); sys.path.insert(0,"baseline_pkg")
from proto_v6 import Fast, load
from flashtext import KeywordProcessor as Base
kws=[l.strip() for l in open("data/kw_48k.txt",encoding="utf-8") if l.strip()]
b=load(Base,kws,False); f=Fast(b)
s=open("data/doc_20000.txt",encoding="utf-8").read().lower()
def tm(label,fn,n=13):
    for _ in range(2): fn()
    xs=[]
    for _ in range(n):
        t0=time.perf_counter(); fn(); xs.append(time.perf_counter()-t0)
    print("%-38s %7.3f ms"%(label,statistics.median(xs)*1e3))

def v_a():
    st=f.starts; toks=[(m.group(),m.start(),m.end()) for m in f.pat.finditer(s)]
    c=0
    for i,t in enumerate(toks):
        g=st.get(t[0])
        if g is not None and (not g or (i+1<len(toks) and toks[i+1][0] in g)): c+=1
    return c
def v_b():
    st=f.starts
    toks=[m.group() for m in f.pat.finditer(s)]
    c=0
    for i in range(len(toks)-1):
        g=st.get(toks[i])
        if g is not None and (not g or toks[i+1] in g): c+=1
    return c
def v_c():
    st=f.starts; get=st.get
    toks=[m.group() for m in f.pat.finditer(s)]
    n=len(toks); c=0
    for i in range(n):
        g=get(toks[i])
        if g is None: continue
        if not g or (i+1<n and toks[i+1] in g): c+=1
    return c
def v_d():
    # only compute single.get; skip gate entirely (measure single-only lower bound)
    g=f.single.get
    return [g(m.group()) for m in f.pat.finditer(s)]
tm("tuples + gate", v_a)
tm("str list + gate", v_b)
tm("str list + gate (cached get)", v_c)
tm("single.get only (no positions)", v_d)
tm("tokenize only (str)", lambda: [m.group() for m in f.pat.finditer(s)])
