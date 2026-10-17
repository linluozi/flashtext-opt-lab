import sys
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor
import re

kp = KeywordProcessor()
for line in open("data/kw_10k.txt", encoding="utf-8"):
    w=line.strip()
    if w: kp.add_keyword(w)
doc = open("data/doc_20000.txt", encoding="utf-8").read()

# instrument by re-implementing with counters (copy of exact path, max_cost=0)
nb = kp.non_word_boundaries
KW = kp._keyword
def counted(s):
    c = dict(outer=0, boundary=0, wordchar=0, enter_inner=0, inner=0, skip=0, root_miss=0, match=0)
    current_dict = kp.keyword_trie_dict
    idx = 0; N = len(s); reset=False; start=0
    while idx < N:
        c['outer'] += 1
        char = s[idx]
        if char not in nb:
            c['boundary'] += 1
            if KW in current_dict or char in current_dict:
                if KW in current_dict: c['match'] += 1
                if char in current_dict:
                    c['enter_inner'] += 1
                    cd2 = current_dict[char]
                    idy = idx+1
                    while idy < N:
                        c['inner'] += 1
                        ic = s[idy]
                        if ic not in nb and KW in cd2: pass
                        if ic in cd2: cd2 = cd2[ic]
                        else: break
                        idy += 1
                current_dict = kp.keyword_trie_dict
                reset = True
            else:
                current_dict = kp.keyword_trie_dict; reset = True
        elif char in current_dict:
            c['wordchar'] += 1
            current_dict = current_dict[char]
        else:
            c['root_miss'] += 1
            current_dict = kp.keyword_trie_dict; reset = True
            idy = idx+1
            while idy < N:
                c['skip'] += 1
                if s[idy] not in nb: break
                idy += 1
            idx = idy
        idx += 1
    return c

c = counted(doc)
print("N =", len(doc))
for k,v in c.items(): print("  %-12s %d" % (k,v))
print("tokens:", len(re.findall(r"[0-9A-Za-z_]+", doc)))
