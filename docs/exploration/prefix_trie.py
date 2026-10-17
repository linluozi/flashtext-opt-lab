"""Prefix trie keyed by token: phrase lookups by successive startswith-free dict hops.
Idea: build a token-level trie of phrase keywords. Walk it token by token using
the already-tokenized list (no char scanning at all). Separators are then
irrelevant, which is exactly the upstream rule: any non-word char separates."""
import sys, re, time, statistics
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as Base
KW='_keyword_'

class Fast:
    def __init__(self, kp):
        self.nwb = kp.non_word_boundaries
        cls=''.join(re.escape(c) for c in sorted(self.nwb))
        self.pat = re.compile('['+cls+']+') if cls else None
        self.ok = self.pat is not None and not any(ch not in self.nwb for ch in kp.keyword_trie_dict)
        if not self.ok: return
        self.single={}
        # token trie: dict of dicts; leaf marker '' -> clean name
        self.tt={}
        self.maxtok=1
        for kw,clean in kp.get_all_keywords().items():
            if any(c not in self.nwb for c in kw):
                toks=self.pat.findall(kw)
                if len(toks)<2:
                    self.ok=False; return
                self.maxtok=max(self.maxtok,len(toks))
                node=self.tt
                for t in toks:
                    node=node.setdefault(t,{})
                node['']=clean
            else:
                self.single[kw]=clean

    def scan(self, s, span_info):
        pat=self.pat
        if span_info:
            toks=[(m.group(),m.start(),m.end()) for m in pat.finditer(s)]
        else:
            toks=[m.group() for m in pat.finditer(s)]
        nt=len(toks)
        single=self.single; get=single.get; tt=self.tt
        out=[]; ap=out.append
        i=0
        while i<nt:
            tok = toks[i][0] if span_info else toks[i]
            v=get(tok)
            adv=1
            node=tt.get(tok)
            if node is not None:
                # longest phrase starting here
                j=i+1; best=None; besttok=1
                while j<nt and j-i<self.maxtok:
                    t2 = toks[j][0] if span_info else toks[j]
                    node=node.get(t2)
                    if node is None: break
                    j+=1
                    if '' in node:
                        best=node['']; besttok=j-i
            else:
                best=None; besttok=1
            if best is not None:
                v=best; adv=besttok
            if v is not None:
                if span_info:
                    st=toks[i][1]; en=toks[i+adv-1][2]
                    ap((v,st,en))
                else:
                    ap(v)
            i+=adv
        return out

def load(cls,kws,cs):
    kp=cls(case_sensitive=cs)
    for k in kws: kp.add_keyword(k)
    return kp
