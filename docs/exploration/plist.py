import sys, re, collections
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as Base
for kwf in ("kw_1k.txt","kw_10k.txt","kw_48k.txt"):
    kp=Base()
    for l in open("data/"+kwf,encoding="utf-8"):
        w=l.strip()
        if w: kp.add_keyword(w)
    nwb=kp.non_word_boundaries
    cls=''.join(re.escape(c) for c in sorted(nwb))
    pat=re.compile('['+cls+']+')
    ph=collections.defaultdict(list)
    for kw in kp.get_all_keywords():
        if any(c not in nwb for c in kw):
            toks=pat.findall(kw)
            if len(toks)>=2: ph[toks[0]].append(kw)
    lens=sorted((len(v) for v in ph.values()), reverse=True)
    print("%-12s first_tokens=%-5d max_list=%d  total=%d  top5=%s" % (kwf,len(ph),lens[0],sum(lens),lens[:5]))
