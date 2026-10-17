import sys, time, statistics
sys.path.insert(0,"bench"); sys.path.insert(0,"baseline_pkg")
from v10 import Fast
from flashtext import KeywordProcessor as Base
big=open("data/doc_20000.txt",encoding="utf-8").read()*10
print("%-12s %-6s %10s %10s %8s" % ("kwset","doc","base ms","v10 ms","speedup"))
for kwf in ("kw_1k.txt","kw_10k.txt","kw_48k.txt"):
    kws=[l.strip() for l in open("data/"+kwf,encoding="utf-8") if l.strip()]
    for name,doc in (("2k",open("data/doc_2000.txt",encoding="utf-8").read()),
                     ("20k",open("data/doc_20000.txt",encoding="utf-8").read()),
                     ("200k",big)):
        b=Base(); [b.add_keyword(k) for k in kws]
        f=Fast(b); s=doc.lower()
        for _ in range(3): b.extract_keywords(doc); f.scan(s,False)
        tb=[];to=[]
        for _ in range(15):
            t0=time.perf_counter(); b.extract_keywords(doc); tb.append(time.perf_counter()-t0)
            t0=time.perf_counter(); f.scan(s,False); to.append(time.perf_counter()-t0)
        mb=statistics.median(tb); mo=statistics.median(to)
        print("%-12s %-6s %10.2f %10.2f %8.2fx" % (kwf,name,mb*1e3,mo*1e3,mb/mo))
