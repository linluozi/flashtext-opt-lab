"""v4: streaming token scan, no intermediate token list."""
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
        self.starts = {}     # first_token -> set(second_token) | empty set == "needs trie walk"
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

    def scan(self, s):
        trie = self.trie; nwb = self.nwb; KWd = KW
        single = self.single; starts = self.starts
        n = len(s)
        out = []; ap = out.append
        consumed = -1
        it = self.pat.finditer(s)
        prev = None          # previous token text
        for m in it:
            start = m.start()
            if start < consumed:
                prev = None
                continue
            tok = m.group()
            v = single.get(tok)
            gate = starts.get(tok)
            if gate is not None:
                # need the following token to decide; peek
                nxt = None
                if not gate:
                    need = True
                else:
                    need = False
                if not need:
                    # look ahead one token
                    save = None
                    try:
                        nm = next(it)
                        nxt = nm.group()
                        save = nm
                    except StopIteration:
                        nxt = None
                    need = nxt is not None and nxt in gate
                    if save is not None and not need:
                        # rewind by handling nm in the next iteration
                        pending = nm
                    else:
                        pending = None
                else:
                    pending = None
                if need:
                    p = start; node = trie; bval = None; bend = -1
                    while p < n:
                        sub = node.get(s[p])
                        if sub is None: break
                        node = sub; p += 1
                        if p == n:
                            if KWd in node: bval = node[KWd]; bend = p
                            break
                        if s[p] not in nwb and KWd in node:
                            bval = node[KWd]; bend = p
                    if bval is not None and (v is None or bend > m.end() - 1):
                        v = bval; end = bend
                    else:
                        end = m.end()
                else:
                    end = m.end()
            else:
                end = m.end()
            if v is not None:
                ap((v, start, end))
                consumed = end + 1
            prev = tok
        return out
