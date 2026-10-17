import sys, collections
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as Base
kp=Base()
for l in open("data/kw_10k.txt",encoding="utf-8"):
    w=l.strip()
    if w: kp.add_keyword(w)
doc=open("data/doc_20000.txt",encoding="utf-8").read()
c=collections.Counter()
orig=kp._levenshtein_rec
def wrap(char,node,word,rows,max_cost,depth=0):
    c['rec']+=1
    n_columns=len(word)+1
    c['cells']+=n_columns
    return orig(char,node,word,rows,max_cost,depth)
kp._levenshtein_rec=wrap
c['rec']=0; c['cells']=0
kp.extract_keywords(doc,max_cost=1)
print("rec calls:",c['rec'],"cells:",c['cells'],"avg cols:",c['cells']/max(1,c['rec']))
# how many trie nodes total?
def count_nodes(d):
    n=1
    for k,v in d.items():
        if k!='_keyword_': n+=count_nodes(v)
    return n
print("trie nodes:",count_nodes(kp.keyword_trie_dict))
print("keywords:",len(kp))
