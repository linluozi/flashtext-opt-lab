"""v9: single-token dict + char-nested phrase trie keyed only on phrase entries.
The char walk here only runs for tokens that start a known phrase, and it uses
.get() (no membership test), stopping at the first miss."""
import sys, re, time, statistics
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as Base
KW='_keyword_'

class Fast:
    def __init__(self, kp):
        self.nwb = kp.non_word_boundaries
        cls = ''.join(re.escape(c) for c in sorted(self.nwb))
        self.pat = re.compile('[' + cls + ']+') if cls else None
        self.ok = self.pat is not None and not any(ch not in self.nwb for ch in kp.keyword_trie_dict)
        if not self.ok: return
        self.single = {}
        self.ph = {}          # char trie over phrase keywords only
        self.tails = {}
        self.maxtok = 1
        for kw, clean in kp.get_all_keywords().items():
            if any(c not in self.nwb for c in kw):
                toks = self.pat.findall(kw)
                if len(toks) >= 2:
                    self.maxtok = max(self.maxtok, len(toks))
                    node = self.ph
                    for ch in kw:
                        node = node.setdefault(ch, {})
                    node[KW] = (clean, len(toks))
                else:
                    self.tails.setdefault(toks[0], []).append((kw, clean))
            else:
                self.single[kw] = clean

    def scan(self, s, span_info):
        toks = [(m.group(), m.start(), m.end()) for m in self.pat.finditer(s)]
        nt = len(toks)
        get = self.single.get
        ph = self.ph; tget = self.tails
        n = len(s); nwb = self.nwb; KWd = KW
        out = []; ap = out.append
        i = 0
        while i < nt:
            tok, st, en = toks[i]
            v = get(tok); adv = 1
            node = ph.get(tok[0])
            if node is not None:
                # walk the phrase trie from st+1 (node already covers s[st])
                p = st + 1; node2 = node; best = None; bend = -1; btok = 0
                while p < n:
                    ch = s[p]
                    # upstream records a candidate when the next char ends a word
                    if ch not in nwb and KWd in node2:
                        best = node2[KWd][0]; bend = p; btok = node2[KWd][1]
                    sub = node2.get(ch)
                    if sub is None:
                        break
                    node2 = sub; p += 1
                if p >= n and KWd in node2:
                    best = node2[KWd][0]; bend = n; btok = node2[KWd][1]
                if best is not None and bend >= en:
                    v = best; en = bend; adv = btok
            else:
                tlist = tget.get(tok)
                if tlist is not None:
                    for kw, clean in tlist:
                        if s.startswith(kw, st):
                            end = st + len(kw)
                            if end == n or s[end] not in nwb:
                                if end >= en:
                                    v = clean; en = end
                                break
            if v is not None:
                if span_info: ap((v, st, en))
                else: ap(v)
            i += adv
        return out
