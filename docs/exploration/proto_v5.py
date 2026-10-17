"""v5: tight token-dict scan. findall for non-span, finditer for span.
Phrase candidates still use the char trie (to honour separator chars exactly),
but only when the first two tokens form a known phrase prefix."""
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
        stack = [(self.trie, '')]
        while stack:
            node, pfx = stack.pop()
            for ch, child in node.items():
                if ch == KW:
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

    def _walk(self, s, start):
        """Char trie walk from `start`; returns (value, end, ntokens) or None."""
        trie = self.trie; nwb = self.nwb; KWd = KW
        n = len(s)
        node = trie
        p = start
        bval = None; bend = -1; btok = 0
        toks = 1
        while p < n:
            sub = node.get(s[p])
            if sub is None:
                break
            node = sub
            p += 1
            if p == n:
                if KWd in node:
                    bval = node[KWd]; bend = p; btok = toks
                break
            if s[p] not in nwb:
                if KWd in node:
                    bval = node[KWd]; bend = p; btok = toks
                # advance over the separator run
                q = p
                while q < n and s[q] not in nwb:
                    q += 1
                if q >= n:
                    break
                # continue walking from q using the same node
                p = q
                toks += 1
                continue
        return (bval, bend, btok) if bval is not None else None

    def scan(self, s, span_info):
        pat = self.pat; single = self.single; starts = self.starts
        get = single.get
        out = []; ap = out.append
        walk = self._walk
        if span_info:
            toks = [(m.group(), m.start(), m.end()) for m in pat.finditer(s)]
        else:
            toks = pat.findall(s)
        nt = len(toks)
        i = 0
        if span_info:
            while i < nt:
                tok, st, en = toks[i]
                v = get(tok)
                adv = 1
                g = starts.get(tok)
                if g is not None and (not g or (i + 1 < nt and toks[i+1][0] in g)):
                    w = walk(s, st)
                    if w is not None and w[1] >= en:
                        v, en2, adv2 = w
                        en = en2; adv = adv2
                if v is not None:
                    ap((v, st, en))
                i += adv
        else:
            while i < nt:
                tok = toks[i]
                v = get(tok)
                adv = 1
                g = starts.get(tok)
                if g is not None and (not g or (i + 1 < nt and toks[i+1] in g)):
                    w = walk(s, 0)  # placeholder, replaced below
                if v is not None:
                    ap(v)
                i += adv
        return out

def load(cls, kws, cs):
    kp = cls(case_sensitive=cs)
    for k in kws: kp.add_keyword(k)
    return kp
