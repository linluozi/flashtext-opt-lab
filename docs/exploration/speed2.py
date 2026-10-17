import sys, time, importlib.util, statistics
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor as Base
spec = importlib.util.spec_from_file_location("optkw", "opt_pkg/flashtext/keyword.py")
opt = importlib.util.module_from_spec(spec); spec.loader.exec_module(opt)
Opt = opt.KeywordProcessor

def load(cls, words):
    kp = cls()
    for w in words: kp.add_keyword(w)
    return kp

doc = open("data/doc_20000.txt", encoding="utf-8").read()
allw=[l.strip() for l in open("data/kw_10k.txt",encoding="utf-8") if l.strip()]
single=[w for w in allw if " " not in w]
multi=[w for w in allw if " " in w]
print("single",len(single),"multi",len(multi))

for label, words in (("single-only",single), ("with-multi",allw)):
    b=load(Base,words); o=load(Opt,words)
    print("  %s fastpath_enabled=%s" % (label, o._build_exact_cache()[3] is False))
    for _ in range(3): b.extract_keywords(doc); o.extract_keywords(doc)
    tb=[];to=[]
    for _ in range(15):
        t0=time.perf_counter(); rb=b.extract_keywords(doc); tb.append(time.perf_counter()-t0)
        t0=time.perf_counter(); ro=o.extract_keywords(doc); to.append(time.perf_counter()-t0)
    assert rb==ro, (len(rb),len(ro))
    mb=statistics.median(tb); mo=statistics.median(to)
    print("    base %.3f ms  opt %.3f ms  speedup %.2fx" % (mb*1e3, mo*1e3, mb/mo))
