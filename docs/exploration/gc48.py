import sys, time, statistics, gc
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as B
import importlib.util
spec=importlib.util.spec_from_file_location("o","opt_pkg/flashtext/keyword.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
O=m.KeywordProcessor
kws=[l.strip() for l in open("data/kw_48k.txt",encoding="utf-8") if l.strip()]
doc=open("data/doc_20000.txt",encoding="utf-8").read()
b=B(); [b.add_keyword(k) for k in kws]
o=O(); [o.add_keyword(k) for k in kws]
for _ in range(5): b.extract_keywords(doc,span_info=True); o.extract_keywords(doc,span_info=True)
to=[]
for i in range(40):
    t=time.perf_counter(); o.extract_keywords(doc,span_info=True); to.append(time.perf_counter()-t)
print("opt raw:", " ".join("%.2f"%(x*1e3) for x in to))
print("gc counts:", gc.get_count(), "gc thresholds", gc.get_threshold())
