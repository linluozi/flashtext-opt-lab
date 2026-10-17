import sys
sys.path.insert(0,"bench"); sys.path.insert(0,"baseline_pkg")
from v9 import Fast
from flashtext import KeywordProcessor as Base
kws=[l.strip() for l in open("data/kw_1k.txt",encoding="utf-8") if l.strip()]
b=Base()
for k in kws: b.add_keyword(k)
f=Fast(b)
print("ph has 'n'?", 'n' in f.ph, "maxtok",f.maxtok)
s=open("data/doc_20000.txt",encoding="utf-8").read().lower()
st=s.find("next day")
print(repr(s[st-5:st+15]), st)
node=f.ph.get('n')
print("node n keys:", list(node)[:10] if node else None)
# trace
nwb=f.nwb; KWd='_keyword_'
p=st; node2=node; nt_=0; inrun=False; best=None
while p<len(s):
    ch=s[p]
    hit = (ch not in nwb and KWd in node2 and node2[KWd][1]==nt_)
    print("p=%d ch=%r nt_=%d KWd_in=%s want=%s hit=%s" % (p,ch,nt_, KWd in node2, node2.get(KWd,("",None))[1] if KWd in node2 else None, hit))
    sub=node2.get(ch)
    if sub is None: print("  STOP"); break
    node2=sub; p+=1
    if ch in nwb:
        if not inrun:
            inrun=True; nt_+=1
            if nt_>f.maxtok: break
    else: inrun=False
