"""Prototype v3: token index + second-token gate; bit-exact vs upstream."""
import sys, re, time, statistics
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor as Base
KW = '_keyword_'

class Fast:
    def __init__(self, kp):
        self.trie = kp.keyword_trie_dict
        self.nwb = kp.non_word_boundaries
        cls = ''.join(re.escape(c) for c in sorted(self.nwb))
        self.pat = re.compile('[' + cls + ']+') if cls else None
        self.ok = self.pat is not None and not any(ch not in self.nwb for ch in self.trie)
        if not self.ok: return
        self.single = {}
        self.phrase_starts = {}     # first_token -> set(second_token)
        stack = [(self.trie, '')]
        while stack:
            node, pfx = stack.pop()
            for ch, child in node.items():
                if ch == KW:
                    if any(c not in self.nwb for c in pfx):
                        toks = self.pat.findall(pfx)
                        if len(toks) >= 2:
                            self.phrase_starts.setdefault(toks[0], set()).add(toks[1])
                        else:
                            # e.g. 'te-' : a token followed by trailing boundary chars.
                            # Mark it unsafe: any run equal to toks[0] must go to the
                            # trie walk so the trailing boundary chars are honoured.
                            self.phrase_starts.setdefault(toks[0], set())
                    else:
                        self.single[pfx] = child
                else:
                    stack.append((child, pfx + ch))

    def scan(self, s):
        n = len(s)
        toks = [(m.group(), m.start(), m.end()) for m in self.pat.finditer(s)]
        single = self.single; ps = self.phrase_starts
        trie = self.trie; nwb = self.nwb; KWd = KW
        out = []; ap = out.append
        nt = len(toks)
        i = 0
        while i < nt:
            tok, start, end = toks[i]
            best = single.get(tok)
            best_end = end
            gate = ps.get(tok)
            if gate is not None and (not gate or (i + 1 < nt and toks[i+1][0] in gate)):
                node = trie; p = start; bend = -1; bval = None
                while p < n:
                    sub = node.get(s[p])
                    if sub is None: break
                    node = sub; p += 1
                    if p == n:
                        if KWd in node: bval = node[KWd]; bend = p
                        break
                    if s[p] not in nwb and KWd in node:
                        bval = node[KWd]; bend = p
                if bval is not None and bend >= best_end:
                    best = bval; best_end = bend
            if best is not None:
                ap((best, start, best_end))
                # skip tokens consumed by the match
                j = i + 1
                while j < nt and toks[j][1] < best_end:
                    j += 1
                i = j
            else:
                i += 1
        return out

def load(cls, kws, cs):
    kp = cls(case_sensitive=cs)
    for k in kws: kp.add_keyword(k)
    return kp

docs = [open("data/doc_%d.txt" % n, encoding="utf-8").read() for n in (200,2000,20000)]
allw = [l.strip() for l in open("data/kw_10k.txt", encoding="utf-8") if l.strip()]
for kwf in ("kw_1k.txt","kw_10k.txt","kw_48k.txt"):
    kws=[l.strip() for l in open("data/"+kwf,encoding="utf-8") if l.strip()]
    for cs in (False, True):
        b=load(Base,kws,cs); f=Fast(b)
        if not f.ok:
            print("%-12s cs=%-5s FALLBACK" % (kwf,cs)); continue
        bad=0
        for d in docs:
            s = d if cs else d.lower()
            ref = b.extract_keywords(d, span_info=True)
            got = f.scan(s)
            if ref != got:
                bad += 1
                if bad==1:
                    for i in range(min(len(ref),len(got))):
                        if ref[i]!=got[i]:
                            print("   diff@%d ref=%r got=%r ctx=%r"%(i,ref[i],got[i],s[max(0,ref[i][1]-30):ref[i][2]+30])); break
                    else: print("   tail ref=%d got=%d"%(len(ref),len(got)))
        print("%-12s cs=%-5s single=%d ph_starts=%d -> %s" % (kwf,cs,len(f.single),len(f.phrase_starts),"OK" if bad==0 else "%d differ"%bad))

print()
print("=== speed (median of 15, interleaved) ===")
def bench(kws, doc, cs=False, n=15):
    b=load(Base,kws,cs); f=Fast(b)
    s = doc if cs else doc.lower()
    for _ in range(3): b.extract_keywords(doc); f.scan(s)
    tb=[];to=[]
    for _ in range(n):
        t0=time.perf_counter(); b.extract_keywords(doc); tb.append(time.perf_counter()-t0)
        t0=time.perf_counter(); f.scan(s); to.append(time.perf_counter()-t0)
    return statistics.median(tb), statistics.median(to)
big=open("data/doc_20000.txt",encoding="utf-8").read()*10
for kwf in ("kw_1k.txt","kw_10k.txt","kw_48k.txt"):
    kws=[l.strip() for l in open("data/"+kwf,encoding="utf-8") if l.strip()]
    for name,doc in (("2k",open("data/doc_2000.txt",encoding="utf-8").read()),("20k",open("data/doc_20000.txt",encoding="utf-8").read()),("200k",big)):
        mb,mo=bench(kws,doc)
        print("  %-12s %-6s base %8.2f ms  v3 %8.2f ms  %5.2fx" % (kwf,name,mb*1e3,mo*1e3,mb/mo))
