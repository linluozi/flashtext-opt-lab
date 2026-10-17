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
    trie2={}   # (tok0, tok1) -> set(tok2 or '')
    stack=[(trie,'')]
    while stack:
        node,pfx=stack.pop()
        for ch,child in node.items():
            if ch==KW:
                if any(c not in nwb for c in pfx):
                    toks=pat.findall(pfx)
                    if len(toks)>=2:
                        key=(toks[0],toks[1])
                        trie2.setdefault(key,set()).add(toks[2] if len(toks)>2 else '')
            else: stack.append((child,pfx+ch))
    doc=open("data/doc_20000.txt",encoding="utf-8").read().lower()
    toks=pat.findall(doc)
    walked=0
    for i in range(len(toks)):
        g=trie2.get((toks[i], toks[i+1] if i+1<len(toks) else None))
        if g is None: continue
        nxt=toks[i+2] if i+2<len(toks) else ''
        if '' in g or nxt in g: walked+=1
    print("%-12s pairs=%-5d  walks_3tok=%-5d" % (kwf,len(trie2),walked))
