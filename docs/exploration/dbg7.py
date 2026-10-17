import sys
sys.path.insert(0,"bench"); sys.path.insert(0,"baseline_pkg")
from proto_v6 import Fast, load
from flashtext import KeywordProcessor as Base
kws=[l.strip() for l in open("data/kw_1k.txt",encoding="utf-8") if l.strip()]
b=load(Base,kws,False); f=Fast(b)
print("maxlen",f.maxlen,"maxtok",f.maxtok)
print("single has 'next'?", 'next' in f.single)
print("starts has 'next'?", f.starts.get('next'))
print("starts has 'day'?", f.starts.get('day'))
print("kw 'next day'?", 'next day' in b.get_all_keywords())
s=open("data/doc_20000.txt",encoding="utf-8").read().lower()
print(repr(s[890:915]))
