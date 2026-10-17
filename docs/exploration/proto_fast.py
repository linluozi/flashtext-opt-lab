"""Prototype v2: token-dict fast path + trie walk only where a spanning keyword can start."""
import sys, re, time, statistics
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor as Base
KW = '_keyword_'

class Index:
    def __init__(self, kp):
        self.trie = kp.keyword_trie_dict
        self.nwb = kp.non_word_boundaries
        cls = ''.join(re.escape(c) for c in sorted(self.nwb))
        self.pat = re.compile('[' + cls + ']+') if cls else None
        self.ok = True
        if any(ch not in self.nwb for ch in self.trie):
            self.ok = False
            return
        single = {}
        span_first = set()
        stack = [(self.trie, '')]
        while stack:
            node, prefix = stack.pop()
            for ch, child in node.items():
                if ch == KW:
                    if any(c not in self.nwb for c in prefix):
                        # spanning keyword: remember its first word run
                        m = self.pat.match(prefix)
                        span_first.add(m.group() if m else prefix)
                    else:
                        single[prefix] = child
                else:
                    stack.append((child, prefix + ch))
        self.single = single
        self.span_first = span_first

    def scan(self, s):
        trie = self.trie; nwb = self.nwb; n = len(s)
        single = self.single; span_first = self.span_first
        out = []; ap = out.append
        consumed = -1
        for m in self.pat.finditer(s):
            start = m.start()
            if start < consumed:
                continue
            tok = m.group()
            if tok in span_first:
                # full trie walk (may span runs)
                node = trie; best = None; best_end = -1; p = start
                while p < n:
                    sub = node.get(s[p])
                    if sub is None:
                        break
                    node = sub; p += 1
                    if p == n:
                        if KW in node:
                            best = node[KW]; best_end = p
                        break
                    if s[p] not in nwb and KW in node:
                        best = node[KW]; best_end = p
                if best is None:
                    continue
                ap((best, start, best_end)); consumed = best_end + 1
            else:
                v = single.get(tok)
                if v is not None:
                    ap((v, start, m.end())); consumed = m.end() + 1
        return out

def load(cls, kws, cs):
    kp = cls(case_sensitive=cs)
    for k in kws: kp.add_keyword(k)
    return kp

docs = [open("data/doc_%d.txt" % n, encoding="utf-8").read() for n in (200,2000,20000)]
for kwf in ("kw_1k.txt","kw_10k.txt","kw_48k.txt"):
    kws=[l.strip() for l in open("data/"+kwf,encoding="utf-8") if l.strip()]
    for cs in (False, True):
        b = load(Base, kws, cs)
        ix = Index(b)
        if not ix.ok:
            print(kwf, cs, "FALLBACK (keyword starts with boundary char)"); continue
        bad = 0
        for d in docs:
            s = d if cs else d.lower()
            ref = b.extract_keywords(d, span_info=True)
            got = ix.scan(s)
            if ref != got:
                bad += 1
                if bad == 1:
                    for i in range(min(len(ref), len(got))):
                        if ref[i] != got[i]:
                            print("   diff @%d ref=%r got=%r ctx=%r" % (i, ref[i], got[i], s[max(0,ref[i][1]-30):ref[i][2]+30]))
                            break
                    else:
                        print("   tail diff ref=%d got=%d" % (len(ref), len(got)))
        print("%-12s cs=%-5s single=%d span_first=%d -> %s" % (kwf, cs, len(ix.single), len(ix.span_first), "OK" if bad==0 else "%d docs differ" % bad))

print()
print("=== speed (median of 15, interleaved) ===")
def bench(kws, doc, cs=False, n=15):
    b = load(Base, kws, cs); ix = Index(b)
    s = doc if cs else doc.lower()
    for _ in range(3): b.extract_keywords(doc); ix.scan(s)
    tb=[];to=[]
    for _ in range(n):
        t0=time.perf_counter(); b.extract_keywords(doc); tb.append(time.perf_counter()-t0)
        t0=time.perf_counter(); ix.scan(s); to.append(time.perf_counter()-t0)
    return statistics.median(tb), statistics.median(to)
big = open("data/doc_20000.txt",encoding="utf-8").read()*10
for kwf in ("kw_1k.txt","kw_10k.txt","kw_48k.txt"):
    kws=[l.strip() for l in open("data/"+kwf,encoding="utf-8") if l.strip()]
    for name,doc in (("2k",open("data/doc_2000.txt",encoding="utf-8").read()),("20k",open("data/doc_20000.txt",encoding="utf-8").read()),("200k",big)):
        mb,mo=bench(kws,doc)
        print("  %-12s %-6s base %8.2f ms  fast %8.2f ms  %5.2fx" % (kwf,name,mb*1e3,mo*1e3,mb/mo))
