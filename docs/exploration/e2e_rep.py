import sys, time, statistics
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as B
import importlib.util
spec=importlib.util.spec_from_file_location("o","opt_pkg/flashtext/keyword.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
O=m.KeywordProcessor
kws=[l.strip() for l in open("data/kw_10k.txt",encoding="utf-8") if l.strip()]
b=B(); [b.add_keyword(k) for k in kws]
o=O(); [o.add_keyword(k) for k in kws]
for f in ("data/en1661.txt","data/en1342.txt"):
    doc=open(f,encoding="utf-8",errors="replace").read()
    for _ in range(3): b.extract_keywords(doc); o.extract_keywords(doc)
    tb=[];to=[]
    for i in range(15):
        if i%2==0:
            t=time.perf_counter(); b.extract_keywords(doc); tb.append(time.perf_counter()-t)
            t=time.perf_counter(); o.extract_keywords(doc); to.append(time.perf_counter()-t)
        else:
            t=time.perf_counter(); o.extract_keywords(doc); to.append(time.perf_counter()-t)
            t=time.perf_counter(); b.extract_keywords(doc); tb.append(time.perf_counter()-t)
    print("%-16s base med %.1f min %.1f | opt med %.1f min %.1f | med-ratio %.2f min-ratio %.2f"%(
        f.split("/")[-1], statistics.median(tb)*1e3,min(tb)*1e3,statistics.median(to)*1e3,min(to)*1e3,
        statistics.median(tb)/statistics.median(to), min(tb)/min(to)))
