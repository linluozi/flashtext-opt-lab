"""v10: token dict for single-token keywords; (tok0,tok1) pair gate -> short
list of full phrase strings resolved with str.startswith (C level).
Keywords whose separator tail is not a plain token run are handled by `tails`."""
import sys, re, time, statistics
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as Base

class Fast:
    def __init__(self, kp):
        self.nwb = kp.non_word_boundaries
        cls = ''.join(re.escape(c) for c in sorted(self.nwb))
        self.pat = re.compile('[' + cls + ']+') if cls else None
        self.ok = self.pat is not None and not any(ch not in self.nwb for ch in kp.keyword_trie_dict)
        if not self.ok:
            return
        self.single = {}
        self.pairs = {}    # (tok0, tok1) -> [(keyword, clean, ntok)]  sorted len desc
        self.tails = {}    # tok0 -> [(keyword, clean)]  (keyword ends in separators)
        for kw, clean in kp.get_all_keywords().items():
            if any(c not in self.nwb for c in kw):
                toks = self.pat.findall(kw)
                if len(toks) >= 2:
                    self.pairs.setdefault((toks[0], toks[1]), []).append((kw, clean, len(toks)))
                else:
                    self.tails.setdefault(toks[0], []).append((kw, clean))
            else:
                self.single[kw] = clean
        for k in self.pairs:
            self.pairs[k].sort(key=lambda x: -len(x[0]))
        for k in self.tails:
            self.tails[k].sort(key=lambda x: -len(x[0]))

    def scan(self, s, span_info):
        toks = [(m.group(), m.start(), m.end()) for m in self.pat.finditer(s)]
        nt = len(toks)
        get = self.single.get
        pget = self.pairs.get
        tget = self.tails
        out = []; ap = out.append
        n = len(s); nwb = self.nwb
        i = 0
        while i < nt:
            tok, st, en = toks[i]
            v = get(tok); adv = 1
            plist = pget((tok, toks[i + 1][0])) if i + 1 < nt else None
            if plist is not None:
                for kw, clean, ntok in plist:
                    if s.startswith(kw, st):
                        end = st + len(kw)
                        if end == n or s[end] not in nwb:
                            if end >= en:
                                v = clean; en = end; adv = ntok
                            break
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
                if span_info:
                    ap((v, st, en))
                else:
                    ap(v)
            i += adv
        return out
