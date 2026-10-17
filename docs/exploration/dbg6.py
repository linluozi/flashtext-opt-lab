import sys, re
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as Base
KW='_keyword_'
kp=Base(case_sensitive=True)
for w in ["in","in the"]: kp.add_keyword(w)
nwb=kp.non_word_boundaries
trie=kp.keyword_trie_dict
s=" in the x"
start=1
node=trie; p=start; nt_=1; maxtok=2
bval=None;bend=-1
while p<len(s) and nt_<=maxtok:
    sub=node.get(s[p])
    print("p=%d ch=%r sub=%s nt_=%d"%(p,s[p],sub is not None,nt_))
    if sub is None: break
    node=sub; p+=1
    if p==len(s):
        if KWd in node: bval=node[KWd];bend=p
        break
    if s[p] not in nwb:
        if KWd in node: bval=node[KWd];bend=p
        q=p
        while q<len(s) and s[q] not in nwb: q+=1
        if q>=len(s): break
        p=q; nt_+=1
print("bval",bval,"bend",bend,"nt_",nt_)
