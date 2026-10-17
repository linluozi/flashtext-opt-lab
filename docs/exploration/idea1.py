"""Prototype: token-level dict fast path for max_cost==0.

Key insight: for max_cost==0 the trie walk only ever follows the longest
root-anchored path, and every accepted match must end at a non-word char.
=> exact matches are exactly the maximal [0-9A-Za-z_]+ tokens that are keywords,
   with the additional rule that a token PREFIX can also match when the token
   continues past the trie. So: a token matches if it is a keyword, OR any of
   its prefixes is a keyword (longest such prefix wins) -- but only when the
   token's remaining chars are still on the trie path.
"""
import sys, re, time
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor

kp = KeywordProcessor()
for line in open("data/kw_10k.txt", encoding="utf-8"):
    w=line.strip()
    if w: kp.add_keyword(w)
doc = open("data/doc_20000.txt", encoding="utf-8").read()

allkw = kp.get_all_keywords()
TOK = re.compile(r"[0-9A-Za-z_]+")

def v1(s):
    out=[]; ap=out.append; get=allkw.get
    for t in TOK.findall(s):
        v = get(t)
        if v is not None:
            ap(v)
        else:
            for L in range(len(t)-1, 0, -1):
                v = get(t[:L])
                if v is not None:
                    ap(v); break
    return out

ref = kp.extract_keywords(doc)
got = v1(doc)
print("ref", len(ref), "v1", len(got), "equal:", ref==got)
if ref!=got:
    for i,(a,b) in enumerate(zip(ref,got)):
        if a!=b: print("first diff at",i,a,b); break
