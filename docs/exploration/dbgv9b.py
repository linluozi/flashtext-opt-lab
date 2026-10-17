import sys
sys.path.insert(0,"bench"); sys.path.insert(0,"baseline_pkg")
from v9 import Fast
from flashtext import KeywordProcessor as Base
kws=[l.strip() for l in open("data/kw_1k.txt",encoding="utf-8") if l.strip()]
b=Base(); [b.add_keyword(k) for k in kws]
f=Fast(b)
print("'i cannot' in ph path?", end=" ")
node=f.ph.get('i')
print(node and ' ' in node)
# token 'i' is single char; startswith approach would need st+len(tok)
s=open("data/doc_20000.txt",encoding="utf-8").read().lower()
st=s.find("i cannot")
print(repr(s[st-5:st+12]),st)
node=f.ph.get('i')
p=st+1; nt_=0; inrun=False; KWd='_keyword_'; nwb=f.nwb
while p<len(s) and p<st+15:
    ch=s[p]
    print("p=%d ch=%r node_keys=%s nt_=%d" % (p,ch,list(node)[:6],nt_))
    sub=node.get(ch)
    if sub is None: print(" stop"); break
    node=sub; p+=1
    if ch in nwb:
        if not inrun:
            inrun=True; nt_+=1
            if nt_>f.maxtok: break
    else: inrun=False
