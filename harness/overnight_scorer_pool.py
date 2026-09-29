"""Overnight step 2 — run the FROZEN RAGTurk matcher over the full M1 pool
(2,392 gold/pred pairs from full_audit_2026-08-16.jsonl) and detect the two
mechanical defects at scale. No labels, no API, no GPU. Imports the frozen
functions from calibrate_ragturk_matcher.py (single source of truth).
Output: results/overnight_pool_scores.json
"""
import json, os, re, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "cal", os.path.join(HERE, "calibrate_ragturk_matcher.py"))
cal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cal)

POOL = os.path.join(HERE, "results", "full_audit_2026-08-16.jsonl")
OUT = os.path.join(HERE, "results", "overnight_pool_scores.json")

recs = []
with open(POOL, encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        if r.get("event") is None and r.get("ok") and r.get("probe_family") == "M1" \
           and r.get("truth_text") and r.get("raw"):
            recs.append(r)
print(f"M1 pool pairs: {len(recs)}")

rows, defect_decade, defect_shortgold = [], 0, 0
for r in recs:
    gold, pred, q = r["truth_text"], r["raw"], ""
    match, level, sim = cal.matcher(gold, pred, q)
    # defect A: gold contains a decade token (\d+'ler...) -> unreachable-rule trigger
    dec_trigger = bool(re.search(r"\d+'ler", gold))
    if dec_trigger:
        defect_decade += 1
    # defect B: gold <5 chars AND not letter-form/numeric -> hard recall ceiling 0
    g = cal.norm(gold)
    letterform = bool(re.fullmatch(r"[a-e][).:].*", g))
    has_num = bool(cal.nums(g))
    if len(g) < 5 and not letterform and not has_num:
        defect_shortgold += 1
    rows.append({"benchmark": r["benchmark"], "model": r["model"],
                 "item_idx": r["item_idx"], "match": match, "level": level,
                 "sim": round(sim, 4), "gold_n": len(g),
                 "dec_trigger": dec_trigger, "shortgold_ceiling": (len(g) < 5 and not letterform and not has_num)})

from collections import defaultdict
agg = defaultdict(lambda: [0, 0])
for x in rows:
    k = (x["benchmark"], x["model"])
    agg[k][0] += x["match"]; agg[k][1] += 1

print("\npass-rate under FROZEN scorer (match / n, %):")
for k in sorted(agg):
    m, n = agg[k]
    print(f"  {k[0]:18} {k[1]:18} {m:4}/{n:<4} {100*m/n:5.1f}%")

lv = defaultdict(lambda: defaultdict(int))
for x in rows:
    lv[x["benchmark"]][x["level"]] += 1
print("\nlevel histogram per benchmark:")
for b in sorted(lv):
    print(f"  {b:18} {dict(sorted(lv[b].items()))}")

print(f"\ndefect A — decade-token golds (rule unreachable for all of them): {defect_decade}")
print(f"defect B — short-gold (<5 char, non-numeric) hard-zero ceiling: {defect_shortgold}")

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"n_pairs": len(rows), "rows": rows,
               "defect_decade_triggers": defect_decade,
               "defect_shortgold_ceiling": defect_shortgold}, f, ensure_ascii=False)
print("written:", OUT)
