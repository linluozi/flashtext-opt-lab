"""v8: token dict for single-token keywords + startswith for phrases.
Keywords with a trailing separator ('te-', 'is--') are handled by a small
extra pass that checks the exact separator suffix, so the fast path stays
enabled for everything else."""
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
        self.single = {}      # token -> clean
        self.phrases = {}     # first token -> [(keyword, clean, ntok)] sorted by len desc
        self.tails = {}       # first token -> [(keyword, clean)]  keyword == token + separators
        for kw, clean in kp.get_all_keywords().items():
            if any(c not in self.nwb for c in kw):
                toks = self.pat.findall(kw)
                if len(toks) >= 2:
                    self.phrases.setdefault(toks[0], []).append((kw, clean, len(toks)))
                else:
                    self.tails.setdefault(toks[0], []).append((kw, clean))
            else:
                self.single[kw] = clean
        for k in self.phrases:
            self.phrases[k].sort(key=lambda x: -len(x[0]))
        for k in self.tails:
            self.tails[k].sort(key=lambda x: -len(x[0]))

    def scan(self, s, span_info):
        toks = [(m.group(), m.start(), m.end()) for m in self.pat.finditer(s)]
        nt = len(toks)
        get = self.single.get
        pget = self.phrases.get
        tget = self.tails.get
        out = []; ap = out.append
        n = len(s); nwb = self.nwb
        i = 0
        while i < nt:
            tok, st, en = toks[i]
            v = get(tok); adv = 1
            plist = pget(tok)
            if plist is not None:
                for kw, clean, ntok in plist:
                    if s.startswith(kw, st):
                        end = st + len(kw)
                        if end == n or s[end] not in nwb:
                            if end >= en:
                                v = clean; en = end; adv = ntok
                            break
            else:
                tlist = tget(tok)
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
