import sys, time, statistics
sys.path.insert(0,"baseline_pkg")
from flashtext import KeywordProcessor as Base
kp=Base()
for l in open("data/kw_10k.txt",encoding="utf-8"):
    w=l.strip()
    if w: kp.add_keyword(w)
node=kp.keyword_trie_dict['t']
ws=kp._white_space_chars; KW=kp._keyword
stop=ws | {KW}
N=200000
def a():
    return node.keys() & (ws | {KW})
def b():
    return not stop.isdisjoint(node)
def c():
    for k in node:
        if k in stop: return True
    return False
for f,label in ((a,"keys() & (ws|{KW})"),(b,"stop.isdisjoint(node)"),(c,"python for loop")):
    f()
    t0=time.perf_counter()
    for _ in range(N): f()
    print("%-30s %8.1f ns/call" % (label,(time.perf_counter()-t0)/N*1e9))

# min of 3 without tuple
import random
vals=[(random.randrange(10),random.randrange(10),random.randrange(10)) for _ in range(1000)]
def m1(): return [min((x,y,z)) for x,y,z in vals]
def m2():
    out=[]
    for x,y,z in vals:
        m=x
        if y<m: m=y
        if z<m: m=z
        out.append(m)
    return out
for f,label in ((m1,"min(tuple)"),(m2,"manual compare")):
    f()
    t0=time.perf_counter()
    for _ in range(200): f()
    print("%-30s %8.2f us/1000" % (label,(time.perf_counter()-t0)/200*1e6))
