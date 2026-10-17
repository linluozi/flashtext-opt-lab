import sys, re, time, statistics
sys.path.insert(0,"bench"); sys.path.insert(0,"baseline_pkg")
from proto_v6 import Fast, load
from flashtext import KeywordProcessor as Base
kws=[l.strip() for l in open("data/kw_48k.txt",encoding="utf-8") if l.strip()]
b=load(Base,kws,False); f=Fast(b)
s=open("data/doc_20000.txt",encoding="utf-8").read().lower()
toks=[(m.group(),m.start(),m.end()) for m in f.pat.finditer(s)]
nwb=f.nwb; KWd='_keyword_'; maxtok=f.maxtok
targets=[]
for i,t in enumerate(toks):
    g=f.starts.get(t[0])
    if g is not None and (not g or (i+1<len(toks) and toks[i+1][0] in g)):
        targets.append(t)
print("targets",len(targets))

def walk_v6(st):
    node=f.trie; p=st; bval=None;bend=-1;btok=0;nt_=0;inrun=False;n=len(s)
    while p<n:
        ch=s[p]
        if nt_>0 and ch not in nwb and KWd in node:
            bval=node[KWd];bend=p;btok=nt_
        sub=node.get(ch)
        if sub is None: break
        node=sub;p+=1
        if ch in nwb:
            if not inrun:
                inrun=True;nt_+=1
                if nt_>maxtok: break
        else: inrun=False
    if p>=n and KWd in node:
        bval=node[KWd];bend=n;btok=nt_
    return bval,bend

def tm(label,fn,n=9):
    for _ in range(2): fn()
    xs=[]
    for _ in range(n):
        t0=time.perf_counter(); fn(); xs.append(time.perf_counter()-t0)
    print("%-34s %7.3f ms"%(label,statistics.median(xs)*1e3))
tm("walk all targets", lambda: [walk_v6(t[1]) for t in targets])
tm("baseline full extract", lambda: b.extract_keywords(s))
tm("v6 full", lambda: f.scan(s,False))
