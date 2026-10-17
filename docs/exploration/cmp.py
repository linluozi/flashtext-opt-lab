import sys, time, importlib
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor as Base
sys.path.insert(0, "opt_pkg")
import importlib.util
spec = importlib.util.spec_from_file_location("optkw", "opt_pkg/flashtext/keyword.py")
opt = importlib.util.module_from_spec(spec); spec.loader.exec_module(opt)
Opt = opt.KeywordProcessor

def load(cls, kwf, cs=False):
    kp = cls(case_sensitive=cs)
    for line in open(kwf, encoding="utf-8"):
        w=line.strip()
        if w: kp.add_keyword(w)
    return kp

doc = open("data/doc_20000.txt", encoding="utf-8").read()
for kwf in ("kw_1k.txt","kw_10k.txt","kw_48k.txt"):
    for cs in (False, True):
        b=load(Base,"data/"+kwf,cs); o=load(Opt,"data/"+kwf,cs)
        for si in (False, True):
            rb=b.extract_keywords(doc, span_info=si); ro=o.extract_keywords(doc, span_info=si)
            ok = rb==ro
            print("%-12s cs=%-5s span=%-5s equal=%-5s  base=%d opt=%d" % (kwf,cs,si,ok,len(rb),len(ro)))
            if not ok:
                for i,(x,y) in enumerate(zip(rb,ro)):
                    if x!=y: print("   first diff",i,x,y); break
                print("   len diff", len(rb)-len(ro))
