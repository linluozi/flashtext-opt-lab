import sys, re, cProfile, pstats, io, collections
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as Base
KW='_keyword_'
doc=open("data/doc_20000.txt",encoding="utf-8").read()
kws=[l.strip() for l in open("data/kw_10k.txt",encoding="utf-8") if l.strip()]
b=Base()
for k in kws: b.add_keyword(k)
nwb=b.non_word_boundaries; trie=b.keyword_trie_dict
cls=''.join(re.escape(c) for c in sorted(nwb)); pat=re.compile('['+cls+']+')
s=doc.lower()

cnt=collections.Counter()
def scan(s):
    n=len(s); out=[]; ap=out.append; consumed=-1
    for m in pat.finditer(s):
        start=m.start()
        if start<consumed: cnt['skip']+=1; continue
        cnt['start']+=1
        node=trie; best=None; best_end=-1; p=start
        while p<n:
            cnt['walk']+=1
            ch=s[p]; sub=node.get(ch)
            if sub is None: break
            node=sub; p+=1
            if p==n:
                if KW in node: best=node[KW]; best_end=p
                break
            if s[p] not in nwb and KW in node:
                best=node[KW]; best_end=p
        if best is None: continue
        ap((best,start,best_end)); consumed=best_end+1
    return out
r=scan(s)
print("hits",len(r))
for k,v in cnt.items(): print("  ",k,v)
pr=cProfile.Profile(); pr.enable()
for _ in range(10): scan(s)
pr.disable()
o=io.StringIO(); pstats.Stats(pr,stream=o).sort_stats("tottime").print_stats(6); print(o.getvalue())
