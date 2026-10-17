import sys
sys.path.insert(0,"bench"); sys.path.insert(0,"baseline_pkg")
from proto_v6 import Fast, load
from flashtext import KeywordProcessor as Base
kws=[l.strip() for l in open("data/kw_1k.txt",encoding="utf-8") if l.strip()]
b=load(Base,kws,False); f=Fast(b)
s=open("data/doc_20000.txt",encoding="utf-8").read().lower()
i=s.find("next day")
print(repr(s[i-10:i+20]), "pos", i)
print("f.single.get('next')", f.single.get('next'))
print("f.starts.get('next')", f.starts.get('next'))
print("gated?", f.starts.get('next') and 'day' in f.starts['next'])
# run scan and see what it produced around there
out=f.scan(s,True)
for v,a,b2 in out:
    if abs(a-i)<20: print("  got",v,a,b2,repr(s[a:b2]))
