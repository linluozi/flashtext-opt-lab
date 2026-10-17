import sys, re
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
    # gate by (first token, second token) pairs already; add: for phrase starts,
    # record the exact set of allowed *first two chars* of the remainder.
    starts={}
    stack=[(trie,'')]
    while stack:
        node,pfx=stack.pop()
        for ch,child in node.items():
            if ch==KW:
                if any(c not in nwb for c in pfx):
                    toks=pat.findall(pfx)
                    if len(toks)>=2:
                        starts.setdefault(toks[0],{}).setdefault(toks[1],set()).add(pfx)
                else: pass
            else: stack.append((child,pfx+ch))
    doc=open("data/doc_20000.txt",encoding="utf-8").read().lower()
    toks=pat.findall(doc)
    # count how many tokens would pass a "first 2 chars of the phrase" test
    gated=0; gated2=0
    for i,t in enumerate(toks):
        g=starts.get(t)
        if g is None: continue
        if i+1<len(toks) and toks[i+1] in g:
            gated+=1
    print("%-12s starts(first)=%-5d starts(1st+2nd)=%-5d  walks=%-5d" % (kwf,len(starts),sum(len(v) for v in starts.values()),gated))
