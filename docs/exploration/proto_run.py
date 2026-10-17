"""Prototype: run-anchored exact scan. Verify equivalence vs upstream on corpora."""
import sys, re, statistics, time
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor as Base

KW = '_keyword_'

def build_index(kp):
    trie = kp.keyword_trie_dict
    nwb = kp.non_word_boundaries
    cls = ''.join(re.escape(c) for c in sorted(nwb))
    pat = re.compile('[' + cls + ']+')
    # keywords starting with a boundary char would need extra start positions
    starts_boundary = any(ch not in nwb for ch in trie)
    return trie, nwb, pat, starts_boundary

def scan(trie, nwb, pat, s):
    n = len(s)
    out = []
    ap = out.append
    consumed = -1
    for m in pat.finditer(s):
        start = m.start()
        if start < consumed:
            continue
        node = trie
        best = None
        best_end = -1
        p = start
        while p < n:
            ch = s[p]
            sub = node.get(ch)
            if sub is None:
                break
            node = sub
            p += 1
            if p == n:
                if KW in node:
                    best = node[KW]; best_end = p
                break
            if s[p] not in nwb and KW in node:
                best = node[KW]; best_end = p
        if best is None:
            continue
        ap((best, start, best_end))
        consumed = best_end + 1
    return out

def run_case(kws, docs, cs=False):
    b = Base(case_sensitive=cs)
    for k in kws: b.add_keyword(k)
    trie, nwb, pat, sb = build_index(b)
    if sb: return None
    bad = 0
    for d in docs:
        s = d if cs else d.lower()
        ref = b.extract_keywords(d, span_info=True)
        got = scan(trie, nwb, pat, s)
        if ref != got:
            bad += 1
            if bad == 1:
                print("   MISMATCH len ref=%d got=%d" % (len(ref), len(got)))
                for i in range(min(len(ref), len(got))):
                    if ref[i] != got[i]:
                        print("     first diff @%d ref=%r got=%r" % (i, ref[i], got[i]))
                        print("     ctx=%r" % s[max(0,ref[i][1]-40):ref[i][2]+40])
                        break
    return bad

docs = [open("data/doc_%d.txt" % n, encoding="utf-8").read() for n in (200,2000,20000,200000)]
allw = [l.strip() for l in open("data/kw_10k.txt", encoding="utf-8") if l.strip()]
for label, kws in (("all-10k", allw), ("single-only", [w for w in allw if " " not in w])):
    for cs in (False, True):
        r = run_case(kws, docs, cs)
        print("%-12s cs=%-5s -> %s" % (label, cs, "FALLBACK" if r is None else ("OK" if r==0 else "%d docs differ" % r)))

print()
print("=== speed ===")
import time
def bench(kws, doc, cs=False, n=15):
    b = Base(case_sensitive=cs)
    for k in kws: b.add_keyword(k)
    trie, nwb, pat, sb = build_index(b)
    s = doc if cs else doc.lower()
    for _ in range(3):
        b.extract_keywords(doc); scan(trie,nwb,pat,s)
    tb=[];to=[]
    for _ in range(n):
        t0=time.perf_counter(); b.extract_keywords(doc); tb.append(time.perf_counter()-t0)
        t0=time.perf_counter(); scan(trie,nwb,pat,s); to.append(time.perf_counter()-t0)
    mb=statistics.median(tb); mo=statistics.median(to)
    return mb, mo
for kwf in ("kw_1k.txt","kw_10k.txt","kw_48k.txt"):
    kws=[l.strip() for l in open("data/"+kwf,encoding="utf-8") if l.strip()]
    for n in (2000,20000,200000):
        doc=open("data/doc_%d.txt"%n,encoding="utf-8").read() if n!=200000 else open("data/doc_20000.txt",encoding="utf-8").read()*10
        mb,mo=bench(kws,doc)
        print("  %-12s n=%-7d base %8.2f ms  proto %8.2f ms  %5.2fx" % (kwf,len(doc),mb*1e3,mo*1e3,mb/mo))
