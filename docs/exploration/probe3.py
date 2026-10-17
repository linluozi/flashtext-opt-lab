import sys, time, cProfile, pstats, io
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor

kp = KeywordProcessor()
for line in open("data/kw_10k.txt", encoding="utf-8"):
    w=line.strip()
    if w: kp.add_keyword(w)
doc = open("data/doc_20000.txt", encoding="utf-8").read()
for _ in range(2): kp.extract_keywords(doc, max_cost=1)

pr=cProfile.Profile(); pr.enable()
for _ in range(5): kp.extract_keywords(doc, max_cost=1)
pr.disable()
s=io.StringIO(); pstats.Stats(pr,stream=s).sort_stats("tottime").print_stats(10); print(s.getvalue())

# count calls
import collections
cnt=collections.Counter()
orig=kp._levenshtein_rec
def wrapped(char,node,word,rows,max_cost,depth=0):
    cnt['rec']+=1
    return orig(char,node,word,rows,max_cost,depth)
kp._levenshtein_rec=wrapped
cnt['rec']=0
r=kp.extract_keywords(doc,max_cost=1)
print("levenshtein rec calls:",cnt['rec'],"hits",len(r))
