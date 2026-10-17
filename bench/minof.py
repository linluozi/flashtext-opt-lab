import sys, time, statistics
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as B
import importlib.util
spec=importlib.util.spec_from_file_location("o","opt_pkg/flashtext/keyword.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
O=m.KeywordProcessor
print("%-12s %-8s %5s %10s %10s %8s"%("kw","doc","span","base min","opt min","min ratio"))
for kwf in ("kw_1k.txt","kw_10k.txt","kw_48k.txt"):
    kws=[l.strip() for l in open("data/"+kwf,encoding="utf-8") if l.strip()]
    for docf in ("doc_2000.txt","doc_20000.txt","doc_200000.txt"):
        doc=open("data/"+docf,encoding="utf-8").read()
        for si in (False,True):
            b=B(); [b.add_keyword(k) for k in kws]
            o=O(); [o.add_keyword(k) for k in kws]
            for _ in range(3): b.extract_keywords(doc,span_info=si); o.extract_keywords(doc,span_info=si)
            tb=[];to=[]
            for i in range(25):
                t=time.perf_counter(); b.extract_keywords(doc,span_info=si); tb.append(time.perf_counter()-t)
                t=time.perf_counter(); o.extract_keywords(doc,span_info=si); to.append(time.perf_counter()-t)
            print("%-12s %-8s %5s %10.3f %10.3f %8.2fx"%(kwf,docf.replace("doc_","").replace(".txt",""),si,min(tb)*1e3,min(to)*1e3,min(tb)/min(to)))
