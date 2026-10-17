"""End-to-end: whole Gutenberg books, upstream vs optimised."""
import sys, time, statistics, glob, os, hashlib
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as B
import importlib.util
spec=importlib.util.spec_from_file_location("o","opt_pkg/flashtext/keyword.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
O=m.KeywordProcessor

kws=[l.strip() for l in open("data/kw_10k.txt",encoding="utf-8") if l.strip()]
b=B(); [b.add_keyword(k) for k in kws]
o=O(); [o.add_keyword(k) for k in kws]
print("%-14s %9s %10s %10s %8s %10s"%("book","chars","base ms","opt ms","speedup","hits"))
rows=[]
for f in sorted(glob.glob("data/en*.txt")):
    doc=open(f,encoding="utf-8",errors="replace").read()
    rb=b.extract_keywords(doc); ro=o.extract_keywords(doc)
    assert rb==ro, "MISMATCH on %s"%f
    for _ in range(2): b.extract_keywords(doc); o.extract_keywords(doc)
    tb=[];to=[]
    for i in range(7):
        t=time.perf_counter(); b.extract_keywords(doc); tb.append(time.perf_counter()-t)
        t=time.perf_counter(); o.extract_keywords(doc); to.append(time.perf_counter()-t)
    mb=min(tb); mo=min(to)
    rows.append((os.path.basename(f),len(doc),mb,mo,mb/mo,len(rb)))
    print("%-14s %9d %10.1f %10.1f %7.2fx %10d"%(os.path.basename(f),len(doc),mb*1e3,mo*1e3,mb/mo,len(rb)))
print()
print("aggregate min ratio: %.2fx   median: %.2fx"%(min(r[4] for r in rows), statistics.median([r[4] for r in rows])))
