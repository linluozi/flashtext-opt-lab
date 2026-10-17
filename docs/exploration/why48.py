import sys, re, time, statistics
sys.path.insert(0,"bench"); sys.path.insert(0,"baseline_pkg")
from proto_v6 import Fast, load
from flashtext import KeywordProcessor as Base
kws=[l.strip() for l in open("data/kw_48k.txt",encoding="utf-8") if l.strip()]
b=load(Base,kws,False); f=Fast(b)
s=open("data/doc_20000.txt",encoding="utf-8").read().lower()
toks=[(m.group(),m.start(),m.end()) for m in f.pat.finditer(s)]
print("tokens",len(toks),"maxtok",f.maxtok,"single",len(f.single),"starts",len(f.starts))
gate=sum(1 for i,t in enumerate(toks) if t[0] in f.starts and (not f.starts[t[0]] or (i+1<len(toks) and toks[i+1][0] in f.starts[t[0]])))
print("gated walks",gate)
# how long are the walks on average?
import collections
lens=collections.Counter()
for i,t in enumerate(toks):
    g=f.starts.get(t[0])
    if g is not None and (not g or (i+1<len(toks) and toks[i+1][0] in g)):
        # measure chars walked
        node=f.trie; p=t[1]; n=len(s); c=0
        while p<n:
            sub=node.get(s[p])
            if sub is None: break
            node=sub; p+=1; c+=1
        lens[c]+=1
print("walk char-length distribution (top):", lens.most_common(8))
print("avg walk chars", sum(k*v for k,v in lens.items())/max(1,sum(lens.values())))
def tm(label,fn,n=11):
    for _ in range(2): fn()
    xs=[]
    for _ in range(n):
        t0=time.perf_counter(); fn(); xs.append(time.perf_counter()-t0)
    print("%-28s %7.3f ms"%(label,statistics.median(xs)*1e3))
tm("base", lambda: b.extract_keywords(s))
tm("v6", lambda: f.scan(s,False))
tm("tokenize", lambda: [(m.group(),m.start(),m.end()) for m in f.pat.finditer(s)])
