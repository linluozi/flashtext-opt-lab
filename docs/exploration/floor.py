import sys, time, re
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor

kp = KeywordProcessor()
for line in open("data/kw_10k.txt", encoding="utf-8"):
    w=line.strip()
    if w: kp.add_keyword(w)
doc = open("data/doc_20000.txt", encoding="utf-8").read()
N=len(doc)
single = {k:v for k,v in kp.get_all_keywords().items() if ' ' not in k}
print("N",N,"keywords",len(kp),"single-token",len(single))

def bench(label, fn, n=20):
    for _ in range(3): fn()
    t0=time.perf_counter()
    for _ in range(n): r=fn()
    dt=(time.perf_counter()-t0)/n
    print("%-42s %7.3f ms  %6.1f ns/char" % (label, dt*1e3, dt/N*1e9))
    return dt

# floor 1: trivial per-char loop
def trivial():
    c=0
    for ch in doc:
        if ch=='z': c+=1
    return c
# floor 2: C-level tokenize only
tok=re.compile(r"[0-9A-Za-z_]+")
bench("C-level findall (tokenize only)", lambda: tok.findall(doc))
# floor 3: tokenize + dict get loop
def tok_dict():
    out=[]
    ap=out.append
    get=single.get
    for t in tok.findall(doc):
        v=get(t)
        if v is not None: ap(v)
    return out
bench("findall + dict.get per token", tok_dict)
# floor 4: original
bench("original extract_keywords (max_cost=0)", lambda: kp.extract_keywords(doc))
bench("trivial python char loop", trivial)
print("hits orig", len(kp.extract_keywords(doc)), "tok_dict", len(tok_dict()))
