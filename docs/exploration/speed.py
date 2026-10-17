import sys, time, importlib.util, statistics
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor as Base
spec = importlib.util.spec_from_file_location("optkw", "opt_pkg/flashtext/keyword.py")
opt = importlib.util.module_from_spec(spec); spec.loader.exec_module(opt)
Opt = opt.KeywordProcessor

def load(cls, kwf):
    kp = cls()
    for line in open(kwf, encoding="utf-8"):
        w=line.strip()
        if w: kp.add_keyword(w)
    return kp

doc = open("data/doc_20000.txt", encoding="utf-8").read()
print("%-12s %10s %10s %8s" % ("keywords","base ms","opt ms","speedup"))
for kwf in ("kw_1k.txt","kw_10k.txt","kw_48k.txt"):
    b=load(Base,"data/"+kwf); o=load(Opt,"data/"+kwf)
    for _ in range(3): b.extract_keywords(doc); o.extract_keywords(doc)
    tb=[]; to=[]
    for _ in range(15):
        t0=time.perf_counter(); b.extract_keywords(doc); tb.append(time.perf_counter()-t0)
        t0=time.perf_counter(); o.extract_keywords(doc); to.append(time.perf_counter()-t0)
    mb=statistics.median(tb); mo=statistics.median(to)
    print("%-12s %10.3f %10.3f %8.2fx" % (kwf, mb*1e3, mo*1e3, mb/mo))
