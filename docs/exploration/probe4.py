import sys, re, collections
sys.path.insert(0, "baseline_pkg")
from flashtext import KeywordProcessor

kp = KeywordProcessor()
for line in open("data/kw_10k.txt", encoding="utf-8"):
    w=line.strip()
    if w: kp.add_keyword(w)

doc = open("data/doc_20000.txt", encoding="utf-8").read()
calls=[]
orig = kp.levensthein
def wrap(word, max_cost=2, start_node=None):
    calls.append((id(start_node), word, max_cost))
    return orig(word, max_cost, start_node)
kp.levensthein = wrap
kp.extract_keywords(doc, max_cost=1)
print("fuzzy calls:", len(calls))
print("distinct (node,word,cost):", len(set(calls)))
print("distinct words:", len(set(c[1] for c in calls)))
print("top words:", collections.Counter(c[1] for c in calls).most_common(8))
# word stats
words = re.findall(r"[A-Za-z][A-Za-z'\-]*", doc)
print("total word tokens:", len(words), "distinct:", len(set(w.lower() for w in words)))
