"""v7: single-token dict + str.startswith for phrase candidates.
Token positions always available (finditer), so both span and non-span paths
share one code path."""
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
        self.phrases = {}
        for kw, clean in kp.get_all_keywords().items():
            if any(c not in self.nwb for c in kw):
                toks = self.pat.findall(kw)
                if len(toks) < 2:
                    self.ok = False
                    return
                self.phrases.setdefault(toks[0], []).append((kw, clean, len(toks)))
            else:
                self.single[kw] = clean
        for k in self.phrases:
            self.phrases[k].sort(key=lambda x: -len(x[0]))

    def scan(self, s, span_info):
        toks = [(m.group(), m.start(), m.end()) for m in self.pat.finditer(s)]
        nt = len(toks)
        get = self.single.get
        pget = self.phrases.get
        out = []; ap = out.append
        n = len(s); nwb = self.nwb
        i = 0
        while i < nt:
            tok, st, en = toks[i]
            v = get(tok); adv = 1
            plist = pget(tok)
            if plist is not None:
                for kw, clean, ntok in plist:
                    L = len(kw)
                    if s.startswith(kw, st):
                        end = st + L
                        if end == n or s[end] not in nwb:
                            if end >= en:
                                v = clean; en = end; adv = ntok
                            break
            if v is not None:
                if span_info:
                    ap((v, st, en))
                else:
                    ap(v)
            i += adv
        return out
