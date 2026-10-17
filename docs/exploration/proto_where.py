import sys, re, time, statistics, collections
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as Base
KW='_keyword_'
kws=[l.strip() for l in open("data/kw_10k.txt",encoding="utf-8") if l.strip()]
kp=Base()
for k in kws: kp.add_keyword(k)
doc=open("data/doc_20000.txt",encoding="utf-8").read()
low=doc.lower()
nwb=kp.non_word_boundaries
cls=''.join(re.escape(c) for c in sorted(nwb))
pat=re.compile('['+cls+']+')
trie=kp.keyword_trie_dict
single={}; span_first=set()
stack=[(trie,'')]
while stack:
    node,pfx=stack.pop()
    for ch,child in node.items():
        if ch==KW:
            if any(c not in nwb for c in pfx):
                m=pat.match(pfx); span_first.add(m.group() if m else pfx)
            else: single[pfx]=child
        else: stack.append((child,pfx+ch))
print("single",len(single),"span_first",len(span_first))
print("span_first sample",list(span_first)[:8])
toks=[m.group() for m in pat.finditer(low)]
print("tokens",len(toks),"hits span_first",sum(1 for t in toks if t in span_first))
c=collections.Counter(t for t in toks if t in span_first)
print("top span_first tokens",c.most_common(10))

def tm(label,fn,n=15):
    for _ in range(3): fn()
    xs=[]
    for _ in range(n):
        t0=time.perf_counter(); fn(); xs.append(time.perf_counter()-t0)
    print("%-40s %7.3f ms" % (label,statistics.median(xs)*1e3))
tm("base", lambda: kp.extract_keywords(doc))
tm("finditer only", lambda: [m.start() for m in pat.finditer(low)])
tm("tokens + single.get", lambda: [single.get(t) for t in toks])
tm("tokens + span_first check", lambda: [t in span_first for t in toks])
tm("tokens via findall", lambda: pat.findall(low))
