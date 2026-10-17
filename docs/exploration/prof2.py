import sys, importlib.util, cProfile, pstats, io
spec = importlib.util.spec_from_file_location("optkw", "opt_pkg/flashtext/keyword.py")
opt = importlib.util.module_from_spec(spec); spec.loader.exec_module(opt)
kp = opt.KeywordProcessor()
for line in open("data/kw_10k.txt", encoding="utf-8"):
    w=line.strip()
    if w: kp.add_keyword(w)
doc = open("data/doc_20000.txt", encoding="utf-8").read()
kp.extract_keywords(doc)
pr=cProfile.Profile(); pr.enable()
for _ in range(10): kp.extract_keywords(doc)
pr.disable()
s=io.StringIO(); pstats.Stats(pr,stream=s).sort_stats("tottime").print_stats(10); print(s.getvalue())
