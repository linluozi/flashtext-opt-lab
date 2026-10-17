import sys, re, collections
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as Base
KW='_keyword_'
for kwf in ("kw_1k.txt","kw_10k.txt","kw_48k.txt"):
    kp=Base()
    for l in open("data/"+kwf,encoding="utf-8"):
        w=l.strip()
        if w: kp.add_keyword(w)
    nwb=kp.non_word_boundaries
    cls=''.join(re.escape(c) for c in sorted(nwb))
    pat=re.compile('['+cls+']+')
    trie=kp.keyword_trie_dict
    single={}; starts={}
    stack=[(trie,'')]
    while stack:
        node,pfx=stack.pop()
        for ch,child in node.items():
            if ch==KW:
                if any(c not in nwb for c in pfx):
                    toks=pat.findall(pfx)
                    if len(toks)>=2: starts.setdefault(toks[0],set()).add(toks[1])
                    else: starts.setdefault(toks[0],set())
                else: single[pfx]=child
            else: stack.append((child,pfx+ch))
    doc=open("data/doc_20000.txt",encoding="utf-8").read().lower()
    toks=pat.findall(doc)
    walk=sum(1 for i,t in enumerate(toks) if t in starts and (not starts[t] or (i+1<len(toks) and toks[i+1] in starts[t])))
    print("%-12s tokens=%-5d single=%-5d starts=%-5d walk=%-5d (%.0f%% of tokens)" % (kwf,len(toks),len(single),len(starts),walk,100*walk/len(toks)))
