import sys, re, time, statistics
doc = open("data/doc_20000.txt", encoding="utf-8").read()
N=len(doc)
TOK=re.compile(r"[0-9A-Za-z_]+")
kw={}
for line in open("data/kw_10k.txt",encoding="utf-8"):
    w=line.strip()
    if w: kw[w]=w
def t(label, fn, n=25):
    for _ in range(3): fn()
    xs=[]
    for _ in range(n):
        t0=time.perf_counter(); fn(); xs.append(time.perf_counter()-t0)
    m=statistics.median(xs)
    print("%-52s %7.3f ms  %6.1f ns/char" % (label, m*1e3, m/N*1e9))
    return m

def A():
    out=[]; ap=out.append; get=kw.get
    for tok in TOK.findall(doc):
        v=get(tok)
        if v is not None: ap(v)
    return out

def B():
    out=[]; ap=out.append; get=kw.get
    for m in TOK.finditer(doc):
        v=get(m.group())
        if v is not None: ap((v,m.start(),m.end()))
    return out

def C():
    out=[]; ap=out.append; get=kw.get
    pos=0; find=TOK.match; n=len(doc)
    # manual scan using match at each position -> likely slower
    while pos<n:
        m=find(doc,pos)
        if m is None: break
        v=get(m.group())
        if v is not None: ap(v)
        pos=m.end()
    return out

t("findall + get (no span)", A)
t("finditer + group + start/end (span)", B)
t("match-at-pos loop", C)
