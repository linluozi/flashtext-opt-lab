import sys, re, time
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor

def build(kwf):
    kp = KeywordProcessor()
    for line in open(kwf, encoding="utf-8"):
        w=line.strip()
        if w: kp.add_keyword(w)
    return kp

doc = open("data/doc_20000.txt", encoding="utf-8").read()
for kwf in ("kw_1k.txt","kw_10k.txt","kw_48k.txt"):
    kp = build("data/"+kwf)
    kws = sorted(kp.get_all_keywords(), key=len, reverse=True)
    body = "|".join(re.escape(k) for k in kws)
    t0=time.perf_counter()
    pat = re.compile(r"(?<![0-9A-Za-z_])(?:" + body + r")(?![0-9A-Za-z_])", re.I)
    tbuild=time.perf_counter()-t0
    s=doc
    t0=time.perf_counter()
    for _ in range(5): got=[m.group() for m in pat.finditer(s)]
    dt=(time.perf_counter()-t0)/5
    ref=[t.lower() for t in kp.extract_keywords(s)]
    print("%-12s n=%-6d build=%.1f ms  scan=%.2f ms  hits=%d/%d equal=%s" % (
        kwf, len(kws), tbuild*1e3, dt*1e3, len(got), len(ref), got==ref))
