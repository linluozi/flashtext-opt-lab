import sys, time, statistics
sys.path.insert(0,"bench"); sys.path.insert(0,"baseline_pkg")
from v9 import Fast
from flashtext import KeywordProcessor as Base
docs=[open("data/doc_%d.txt"%n,encoding="utf-8").read() for n in (200,2000,20000)]
for kwf in ("kw_1k.txt","kw_10k.txt","kw_48k.txt"):
    kws=[l.strip() for l in open("data/"+kwf,encoding="utf-8") if l.strip()]
    for cs in (False,True):
        b=Base(case_sensitive=cs)
        for k in kws: b.add_keyword(k)
        f=Fast(b)
        if not f.ok: print(kwf,cs,"FALLBACK"); continue
        bad=0
        for d in docs:
            s=d if cs else d.lower()
            ref=b.extract_keywords(d,span_info=True); got=f.scan(s,True)
            if ref!=got:
                bad+=1
                if bad==1:
                    for i in range(min(len(ref),len(got))):
                        if ref[i]!=got[i]:
                            print("  diff@%d ref=%r got=%r ctx=%r"%(i,ref[i],got[i],s[max(0,ref[i][1]-30):ref[i][2]+30]));break
                    else: print("  tail ref=%d got=%d"%(len(ref),len(got)))
        print("%-12s cs=%-5s -> %s"%(kwf,cs,"OK" if bad==0 else "%d differ"%bad))
