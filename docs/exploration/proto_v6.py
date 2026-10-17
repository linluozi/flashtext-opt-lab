"""v6: token index + 2-token gate + trie walk bounded by max keyword length."""
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
        self.starts = {}
        self.maxlen = 0
        self.maxtok = 1
        stack = [(self.trie, '')]
        while stack:
            node, pfx = stack.pop()
            for ch, child in node.items():
                if ch == KW:
                    self.maxlen = max(self.maxlen, len(pfx))
                    self.maxtok = max(self.maxtok, len(self.pat.findall(pfx)))
                    if any(c not in self.nwb for c in pfx):
                        toks = self.pat.findall(pfx)
                        if len(toks) >= 2:
                            self.starts.setdefault(toks[0], set()).add(toks[1])
                        else:
                            self.starts.setdefault(toks[0], set())
                    else:
                        self.single[pfx] = child
                else:
                    stack.append((child, pfx + ch))

    def scan(self, s, span_info):
        pat = self.pat; single = self.single; starts = self.starts
        get = single.get
        trie = self.trie; nwb = self.nwb; KWd = KW
        maxlen = self.maxlen; maxtok = self.maxtok
        n = len(s)
        out = []; ap = out.append
        toks = [(m.group(), m.start(), m.end()) for m in pat.finditer(s)]
        nt = len(toks)
        i = 0
        while i < nt:
            tok, st, en = toks[i]
            v = get(tok)
            adv = 1
            g = starts.get(tok)
            if g is not None and (not g or (i + 1 < nt and toks[i+1][0] in g)):
                # char trie walk: one char at a time so separators are honoured
                # exactly like upstream.  Stop once more than maxtok word runs
                # have been started (no keyword can be longer than that).
                node = trie; p = st; bval = None; bend = -1; btok = 0
                nt_ = 0; inrun = False
                while p < n:
                    ch = s[p]
                    # upstream records a candidate when the NEXT char ends the word
                    if nt_ > 0 and ch not in nwb and KWd in node:
                        bval = node[KWd]; bend = p; btok = nt_
                    sub = node.get(ch)
                    if sub is None:
                        break
                    node = sub; p += 1
                    if ch in nwb:
                        if not inrun:
                            inrun = True; nt_ += 1
                            if nt_ > maxtok:
                                break
                    else:
                        inrun = False
                if p >= n and KWd in node:
                    bval = node[KWd]; bend = n; btok = nt_
                if bval is not None and bend >= en:
                    v = bval; en = bend; adv = btok if btok > 0 else 1
            if v is not None:
                if span_info: ap((v, st, en))
                else: ap(v)
            i += adv
        return out

def load(cls, kws, cs):
    kp = cls(case_sensitive=cs)
    for k in kws: kp.add_keyword(k)
    return kp
