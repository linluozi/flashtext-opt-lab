import sys, re, time, statistics
doc = open("data/doc_20000.txt", encoding="utf-8").read()
N=len(doc)
TOK=re.compile(r"[0-9A-Za-z_]+")
kw=set(open("data/kw_10k.txt",encoding="utf-8").read().split())
def t(label, fn, n=20):
    for _ in range(3): fn()
    xs=[]
    for _ in range(n):
        t0=time.perf_counter(); fn(); xs.append(time.perf_counter()-t0)
    m=statistics.median(xs)
    print("%-46s %7.3f ms  %6.1f ns/char" % (label, m*1e3, m/N*1e9))
t("findall", lambda: TOK.findall(doc))
t("finditer + group", lambda: [m.group() for m in TOK.finditer(doc)])
t("finditer + start/end", lambda: [(m.start(),m.end()) for m in TOK.finditer(doc)])
t("finditer + group + get", lambda: [kw.__contains__(m.group()) for m in TOK.finditer(doc)])
def via_findall_pos():
    out=[]; ap=out.append; pos=0
    for s in TOK.findall(doc):
        i=doc.index(s,pos); pos=i+len(s); ap((s,i))
    return out
t("findall + str.index", via_findall_pos)
t("split on non-word", lambda: re.split(r"[^0-9A-Za-z_]+", doc))
