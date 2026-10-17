import sys, re
sys.path.insert(0,"bench"); sys.path.insert(0,"baseline_pkg")
from proto_v6 import Fast, load
from flashtext import KeywordProcessor as Base
kws=[l.strip() for l in open("data/kw_1k.txt",encoding="utf-8") if l.strip()]
b=load(Base,kws,False); f=Fast(b)
s=open("data/doc_20000.txt",encoding="utf-8").read().lower()
st=s.find("next day")
trie=f.trie; nwb=f.nwb; KWd='_keyword_'
node=trie; p=st; nt_=0; inrun=False; bval=None;bend=-1;btok=0
trace=[]
while p<len(s):
    ch=s[p]; sub=node.get(ch)
    trace.append((p,repr(ch),sub is not None,nt_))
    if sub is None: break
    node=sub; p+=1
    if ch in nwb:
        if not inrun:
            inrun=True; nt_+=1
            if nt_>f.maxtok: break
    else:
        inrun=False
        if KWd in node: bval=node[KWd]; bend=p; btok=nt_
for t in trace[:20]: print(t)
print("bval",bval,"bend",bend,"btok",btok,"maxtok",f.maxtok)
print("trie has space after next?", ' ' in trie['n']['e']['x']['t'])
