import sys, time, statistics, re
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as Base
kws=[l.strip() for l in open("data/kw_10k.txt",encoding="utf-8") if l.strip()]
b=Base()
for k in kws: b.add_keyword(k)
def tm(doc,label):
    for _ in range(2): b.extract_keywords(doc)
    xs=[]
    for _ in range(11):
        t0=time.perf_counter(); b.extract_keywords(doc); xs.append(time.perf_counter()-t0)
    m=statistics.median(xs)
    print("%-40s n=%-7d %8.3f ms  %6.1f ns/char" % (label,len(doc),m*1e3,m/len(doc)*1e9))
doc20=open("data/doc_20000.txt",encoding="utf-8").read()
tm(doc20,"real prose")
tm(" ".join(["word"]*3600),"all same common word")
tm(" ".join(["zzzz"]*3600),"all out-of-vocab")
tm("z"*20000,"single long token")
tm("a"*20000,"single long token 'a'")
tm(" ".join(["a"]*10000),"single-char tokens")
tm("中"*20000,"CJK run (no boundaries)")
tm("中 文 "*4000,"CJK spaced")
tm("the "*4000,"space-only, keyword 'the'")
tm("\n"*20000,"newlines")
