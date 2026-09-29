"""Overnight step 3 — quantify what the mechanical defects cost each leaderboard cell.

Repair ladder (09-20 pilot, deepdive_2026-09-20.md §2.3):
  R1 apostrophe-preserving normalization (frozen norm strips ' -> decade rule dead);
  R2 letter-dot abbreviation fold (M.S. -> ms; actual cause of 2 failures);
  R3 short-gold numeric bypass (gold <5 chars non-numeric: frozen ceiling = 0);
  R4 decade regex matches the preserved apostrophe: (\\d+)ler -> (\\d+)'ler.
matcher_repaired is the FROZEN matcher with exactly two token diffs:
  cal.norm -> norm_r2  (R1+R2)  and  r"(\\d+)ler" -> r"(\\d+)'ler"  (R4),
plus the R3 bypass in front. Every threshold byte-identical.
Verify on the frozen 106 labeled pairs: TP 17 / FP 0 / TN 71 / FN 18
(recall 0.371 -> 0.486, precision 1.000 — 4 repairs, zero false accepts).
"""
import json, os, re, csv, random, sys, unicodedata, importlib.util
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "cal", os.path.join(HERE, "calibrate_ragturk_matcher.py"))
cal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cal)

def norm_r2(s: str) -> str:
    """R1: apostrophes survive; R2: letter-dot abbreviation fold m.s. -> ms."""
    s = unicodedata.normalize("NFC", str(s))
    s = re.sub(r"[\*\#\_\`>]", " ", s)
    s = re.sub(r"\s+", " ", s.lower()).strip()
    s = s.replace("\u2019", "'")
    s = re.sub(r"[^\w\s\d.,:°/%'-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"\b(?:[a-z]\.\s*)+[a-z]\.?\b", lambda m: m.group(0).replace(".", ""), s)

def matcher_repaired(gold: str, pred: str, question: str = "") -> tuple:
    """Frozen cascade, two-token diff (norm->norm_r2, decade regex), R3 bypass in front."""
    g, p = norm_r2(gold), norm_r2(pred)
    if not g or not p: return (False, "empty", 0.0)
    # R3: short numeric gold (<5 chars, not letter-form): the number IS the answer
    letterform = bool(re.fullmatch(r"[a-e][).:].*", g))
    if len(g) < 5 and not letterform:
        gn0 = cal.nums(g)
        if gn0:
            if all(t in cal.nums(p) for t in gn0): return (True, "shortgold-num", 1.0)
            return (False, "shortgold-num-miss", 0.0)
    if re.fullmatch(r"[a-e][).:].*", g):
        if re.match(r"[a-e][).:]", p): return (True, "letter", 1.0)
        return (False, "letter-mismatch", 0.0)
    if g == p: return (True, "exact", 1.0)
    gn, pn = cal.nums(g), cal.nums(p)
    if gn:
        for t in gn:
            dec = re.search(r"(\d+)'ler", g)            # R4: apostrophe now preserved
            if dec and dec.group(1) == t:
                if not any(int(pv) in range(int(t), int(t)+10) for pv in pn):
                    return (False, "number-mismatch", 0.0)
            elif t not in pn:
                return (False, "number-mismatch", 0.0)
    if len(g) >= 8 and g in p:
        return (True, "containment", 1.0) if len(g)/max(len(p),1) >= 0.25 else (False, "containment-thin", 0.0)
    if len(p) >= 8 and p in g:
        return (True, "containment", 1.0) if len(p)/max(len(g),1) >= 0.25 else (False, "containment-thin", 0.0)
    gs, ps = set(g.split()), set(p.split())
    jac = len(gs & ps)/len(gs | ps) if gs and ps else 0.0
    cov = len(cal.grams5(g) & cal.grams5(p))/len(cal.grams5(g)) if cal.grams5(g) else 0.0
    sim = max(jac, cov)
    q = norm_r2(question)
    dist = cal.grams5(g) - cal.grams5(q) if q else set(cal.grams5(g))
    dcov = len(dist & cal.grams5(p))/len(dist) if dist else 0.0
    TR_STOP = {"bir","ve","ile","için","daha","sonra","kendi","olarak","göre",
               "ancak","ayrıca","bu","şu","o","ne","hangi","nasıl","neden",
               "ilk","kez","ise","da","de","mı","mi","mu","mü","ki","ya","en"}
    q_toks = set(q.split()) if q else set()
    dtoks = [t for t in g.split() if len(t) >= 4 and t not in TR_STOP and t not in q_toks]
    tok_guard = (len(dtoks) <= 4 and all(t in ps for t in dtoks)) or \
                (len(dtoks) > 4 and sum(1 for t in dtoks if t in ps)/len(dtoks) >= 0.5)
    if len(g) > 120 and not gn:
        if dcov >= 0.50 and jac >= 0.30:
            return (True, "paraphrase-distinctive", dcov)
    t_jac, t_cov = (0.65, 0.80) if not gn else (0.55, 0.65)
    if (jac >= t_jac or cov >= t_cov) and (not dist or dcov >= 0.50) and tok_guard:
        return (True, "paraphrase", sim)
    return (False, "none", sim)

def verify():
    recs = [json.loads(l) for l in open(os.path.join(HERE, "results", "pilot_audit_2026-08-16.jsonl"), encoding="utf-8") if l.strip()]
    raw = list(csv.DictReader(open(os.path.join(HERE, "data", "ragturk_formal5k.csv"), encoding="utf-8")))
    samp = random.Random(42).sample(raw, 50)
    bykey = {(r["model"], r["probe"], r["item_idx"]): r for r in recs
             if r["benchmark"] == "ragturk_formal5k" and r["probe"] in ("M2b_A", "M2b_B")}
    conf = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}
    for model, probe, item, label in cal.LABELS:
        r = bykey.get((model, probe, item))
        if r is None: continue
        gold, pred, q = samp[item].get("cevap") or "", r.get("raw") or "", samp[item].get("soru") or ""
        match, _, _ = matcher_repaired(gold, pred, q)
        if match and label == 1: conf["tp"] += 1
        elif match and label == 0: conf["fp"] += 1
        elif not match and label == 0: conf["tn"] += 1
        else: conf["fn"] += 1
    tp, fp, tn, fn = conf["tp"], conf["fp"], conf["tn"], conf["fn"]
    rec_ = tp/(tp+fn) if tp+fn else 0
    prec = tp/(tp+fp) if tp+fp else 0
    ok = (tp, fp, tn, fn) == (17, 0, 71, 18)
    print(f"VERIFY repaired cascade: TP={tp} FP={fp} TN={tn} FN={fn} "
          f"precision={prec:.3f} recall={rec_:.3f}  ->  {'PASS' if ok else 'FAIL (expected 17/0/71/18)'}")
    return ok

def pool_deltas():
    d = json.load(open(os.path.join(HERE, "results", "overnight_pool_scores.json"), encoding="utf-8"))
    rows = d["rows"]
    recs = []
    for line in open(os.path.join(HERE, "results", "full_audit_2026-08-16.jsonl"), encoding="utf-8"):
        r = json.loads(line)
        if r.get("event") is None and r.get("ok") and r.get("probe_family") == "M1" \
           and r.get("truth_text") and r.get("raw"):
            recs.append(r)
    agg = defaultdict(lambda: {"frozen": 0, "repaired": 0, "n": 0})
    for r, x in zip(recs, rows):
        k = (r["benchmark"], r["model"])
        agg[k]["n"] += 1
        agg[k]["frozen"] += x["match"]
        m, _, _ = matcher_repaired(r["truth_text"], r["raw"], "")
        agg[k]["repaired"] += m
    print("\ncell deltas (frozen % -> repaired %):")
    deltas = {}
    for k in sorted(agg):
        a = agg[k]
        pf, pr = 100*a["frozen"]/a["n"], 100*a["repaired"]/a["n"]
        deltas[f"{k[0]}|{k[1]}"] = {"frozen_pct": round(pf,1), "repaired_pct": round(pr,1),
                                    "delta_pp": round(pr-pf,1), "n": a["n"]}
        print(f"  {k[0]:18} {k[1]:18} {pf:5.1f} -> {pr:5.1f}  ({pr-pf:+.1f} pp)")
    print("\nleaderboard per benchmark:")
    flips = []
    bybm = defaultdict(list)
    for key, v in deltas.items():
        bybm[key.split("|")[0]].append((v["repaired_pct"], key, v["frozen_pct"]))
    for bm in sorted(bybm):
        order_old = sorted(bybm[bm], key=lambda t: -t[2])
        order_new = sorted(bybm[bm], key=lambda t: -t[0])
        flipped = [o[1] for o in order_old] != [o[1] for o in order_new]
        if flipped: flips.append(bm)
        print(f"  {bm:18} {'FLIP' if flipped else 'same'}  " +
              " > ".join(f"{k.split('|')[1]}:{p:.1f}" for p, k, _ in order_new))
    out = os.path.join(HERE, "results", "overnight_repair_deltas.json")
    json.dump({"cells": deltas, "leaderboard_flips": flips}, open(out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("\nwritten:", out)

if __name__ == "__main__":
    if not verify():
        sys.exit("verification failed — repair ladder does not reproduce the pilot; stopping")
    pool_deltas()
