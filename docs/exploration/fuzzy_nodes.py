import sys, collections
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as Base
kp=Base()
for l in open("data/kw_10k.txt",encoding="utf-8"):
    w=l.strip()
    if w: kp.add_keyword(w)
doc=open("data/doc_20000.txt",encoding="utf-8").read()
c=collections.Counter()
orig=kp.levensthein
def wrap(word, max_cost=2, start_node=None):
    c['calls']+=1
    c['root' if start_node is kp.keyword_trie_dict else 'deep']+=1
    c['wordlen']+=len(word)
    c['empty' if not word else 'nonempty']+=1
    for x in orig(word,max_cost,start_node): 
        c['yield']+=1
        yield x
kp.levensthein=wrap
kp.extract_keywords(doc,max_cost=1)
for k,v in sorted(c.items()): print("  %-10s %d"%(k,v))
print("avg word len:", c['wordlen']/max(1,c['calls']))
