import sys, time, statistics, importlib
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as B
sys.path.insert(0,"opt_pkg")
import importlib.util
spec=importlib.util.spec_from_file_location("o","opt_pkg/flashtext/keyword.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
O=m.KeywordProcessor
kws=[l.strip() for l in open("data/kw_48k.txt",encoding="utf-8") if l.strip()]
doc=open("data/doc_20000.txt",encoding="utf-8").read()
b=B(); [b.add_keyword(k) for k in kws]
o=O(); [o.add_keyword(k) for k in kws]
for _ in range(5): b.extract_keywords(doc,span_info=True); o.extract_keywords(doc,span_info=True)
tb=[];to=[]
for i in range(40):
    if i%2==0:
        t=time.perf_counter(); b.extract_keywords(doc,span_info=True); tb.append(time.perf_counter()-t)
        t=time.perf_counter(); o.extract_keywords(doc,span_info=True); to.append(time.perf_counter()-t)
    else:
        t=time.perf_counter(); o.extract_keywords(doc,span_info=True); to.append(time.perf_counter()-t)
        t=time.perf_counter(); b.extract_keywords(doc,span_info=True); tb.append(time.perf_counter()-t)
print("base median %.3f ms  (min %.3f max %.3f)"%(statistics.median(tb)*1e3,min(tb)*1e3,max(tb)*1e3))
print("opt  median %.3f ms  (min %.3f max %.3f)"%(statistics.median(to)*1e3,min(to)*1e3,max(to)*1e3))
print("ratio median %.2fx"%(statistics.median(tb)/statistics.median(to)))
print("CV base %.1f%%  opt %.1f%%"%(100*statistics.stdev(tb)/statistics.mean(tb),100*statistics.stdev(to)/statistics.mean(to)))
