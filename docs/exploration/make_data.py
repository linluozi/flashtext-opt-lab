"""Build benchmark inputs from real Project Gutenberg texts (public domain)."""
import re, json, glob, random, os

def strip_g(t):
    m = re.search(r'\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*', t, re.S | re.I)
    if m: t = t[m.end():]
    m = re.search(r'\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*', t, re.S | re.I)
    if m: t = t[:m.start()]
    return t

texts = {}
for f in sorted(glob.glob("data/en*.txt")):
    texts[os.path.basename(f)] = strip_g(open(f, encoding="utf-8", errors="replace").read())

all_text = "\n".join(texts.values())
words = re.findall(r"[A-Za-z][A-Za-z'\-]*", all_text)
freq = {}
for w in words:
    freq[w.lower()] = freq.get(w.lower(), 0) + 1
vocab = [w for w, c in sorted(freq.items(), key=lambda kv: -kv[1]) if len(w) >= 3]

# multi-word phrases drawn from real adjacent tokens (realistic entity-ish entries)
toks = [w.lower() for w in words]
bigrams, trigrams = {}, {}
for i in range(len(toks) - 1):
    k = toks[i] + " " + toks[i + 1]
    bigrams[k] = bigrams.get(k, 0) + 1
for i in range(len(toks) - 2):
    k = toks[i] + " " + toks[i + 1] + " " + toks[i + 2]
    trigrams[k] = trigrams.get(k, 0) + 1
top_bi = [k for k, c in sorted(bigrams.items(), key=lambda kv: -kv[1]) if c >= 3][:6000]
top_tri = [k for k, c in sorted(trigrams.items(), key=lambda kv: -kv[1]) if c >= 2][:3000]

random.seed(20261017)
def build(n_single, n_multi, path):
    kws = vocab[:n_single] + random.sample(top_bi, min(n_multi, len(top_bi)))
    kws = list(dict.fromkeys(kws))
    with open(path, "w", encoding="utf-8") as f:
        for k in kws:
            f.write(k + "\n")
    return len(kws)

print("vocab", len(vocab), "bi", len(top_bi), "tri", len(top_tri))
for n, m, name in [(1000, 200, "kw_1k.txt"), (8000, 2000, "kw_10k.txt"), (40000, 8000, "kw_48k.txt")]:
    c = build(n, m, "data/" + name)
    print(name, c)

# documents at several sizes, sliced from real prose
def slice_doc(chars, seed):
    rnd = random.Random(seed)
    src = all_text
    start = rnd.randrange(0, max(1, len(src) - chars - 1))
    s = src[start:start + chars]
    sp = s.find(" ")
    return s[sp + 1:] if sp > 0 else s

for chars in (200, 2000, 20000, 200000):
    doc = slice_doc(chars, 7 + chars)
    with open("data/doc_%d.txt" % chars, "w", encoding="utf-8") as f:
        f.write(doc)
    print("doc_%d.txt" % chars, len(doc))
