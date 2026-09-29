# scorer-invariance

Artifact repo for the paper **"Precision-First Scorer Invariance: A Two-Token Repair for
Benchmark Answer Matching and Its Measured Effect on Turkish Benchmark Scores"**
(draft: `paper/main_draft_v0.md`; sibling repo: [tr-contamination-audit](https://github.com/oguzcura/tr-contamination-audit)).

**Status (2026-09-30):** draft v0. A precision-first Turkish QA scorer (L0–L6 cascade,
published with hand labels) carries two mechanical defects — apostrophe-stripped
normalization makes the decade rule unreachable (9/2,392 pool golds) and sub-5-char
golds sit under an unreachable similarity ceiling (36/2,392 hard-zeroed). A two-token,
verification-gated repair holds precision at 1.000 and raises recall 0.371 → 0.486
(106-pair labeled set; recall 0.541 on a 159-pair double-adjudicated consensus set,
rater agreement 95.8%, Cohen's κ = 0.902). Re-scoring 12 benchmark×model cells moves
scores by up to **+9.0pp (+12.4% relative)**, 4/12 cells Holm-significant; **no
leaderboard rank flips** — the contribution is measurement validity, not reordering.

## Repository structure

| Path | Contents |
|---|---|
| `pre-registration.md` | Frozen pre-registration (sha256 self-hash in header; Amendment A1 appended) |
| `paper/` | Draft v0 (Markdown; LaTeX conversion pending) |
| `notes/` | Verification note (novelty), house conventions, prereg draft copy, overnight ops log |
| `harness/` | Frozen scorer + calibration, pool scorer, two-token repair script |
| `results/` | All scored/label artifacts the paper numbers trace to (see Reproduction) |
| `data/` | (pending) dataset snapshots + manifest; datasets currently referenced in place |

## Key results

| Result | Value | Artifact |
|---|---|---|
| Frozen scorer on 106 hand labels | P 1.000, R 0.371 (TP 13 FP 0 TN 71 FN 22) | `results/ragturk_matcher_labeled.json` |
| Repaired scorer on same 106 | P 1.000, R 0.486 (TP 17 FP 0 TN 71 FN 18) | `harness/repair_quantify.py` output |
| Defect prevalence (2,392-pair M1 pool) | 45/2,392 = 1.9% (9 decade, 36 short-gold) | `results/overnight_pool_scores.json` |
| Human confirmation of defect cost | 31/45 defect-flagged items (69%) human-confirmed correct | `results/adjudication_analysis_2026-09-30.json` |
| Double adjudication (166 pairs, 2 blind raters) | agreement 159/166 = 95.8%, κ = 0.902, consensus n = 159 | rater CSVs + analysis JSON |
| H1 (recall lift, confirmatory) | PASS — bootstrap 95% CI [0.459, 0.622], seed 42 | `results/step5_hypothesis_tests.json` |
| H2 (benchmark impact, confirmatory) | PASS — 4/12 cells Holm-significant, max +9.0pp; frozen-only discordants a = 0 in all 12 cells | `results/step5_hypothesis_tests.json` |
| Leaderboard flips | none (exploratory pass) | `results/overnight_repair_deltas.json` |

## Method summary

Frozen scorer cascade L0–L6 with hand labels (strict single-pass policy, 2026-08-16;
10-pair agreement batch 10/10) — pre-reg §2 of the sibling audit. Defect detection at
pool scale (2,392 pairs, no API) — pre-reg §0. Two-token repair + verification gate on
the 106-pair set — pre-reg §1.2/H1 precision clause. Double-blind adjudication
(2 raters, strict consensus, seed-42 order randomization) — pre-reg §2. Hypothesis
tests (bootstrap CI; McNemar exact + Holm over the 12-cell family) — pre-reg §3.

## Validation / positive control

The 106-pair labeled set is the fixed reference: the frozen scorer reproduces
13/0/71/22 exactly (pilot re-run), and the repair is admitted only if precision stays
1.000 on that set — verified in the same run that produced the deltas. Rater-2 labeled
the 166-pair package blind (no scorer output, randomized order, seed 42).

## Reproduction

```bash
uv run python harness/overnight_scorer_pool.py     # defect scan over the 2,392-pair pool -> results/overnight_pool_scores.json
uv run python harness/repair_quantify.py           # two-token repair + verification gate -> console matrix (17/0/71/18)
uv run python harness/calibrate_ragturk_matcher.py # frozen scorer vs 106 hand labels -> results/ragturk_matcher_labeled.json
sha256sum pre-registration.md                      # body hash must equal the header value
```

**Spend:** $0.00 — every number in this repo was produced without a single API call
(scoring + labeling + statistics only). No cost cap was needed (pre-reg §0).

## Known honest limitations

- The repair does **not** recover the 45 flagged defect items themselves (0 of the 31
  human-confirmed-correct defect pairs are matched even after repair): the flagged
  decade golds and non-numeric short golds need semantic matching beyond two tokens.
  51 consensus-correct pairs remain missed — paraphrase headroom, not fixed here.
- No M1 rank-order flips among the 3 models: scores move up to +9pp (+12.4% relative)
  from 1.9% of the pool, but leaderboards are unaffected at this prevalence.
- One scorer family, one language (Turkish), one pool, two raters, one rubric; the
  repair is two-token-specific, not a general fix.
- The pre-registration was frozen retroactively relative to step 4 (Amendment A1
  documents this; no threshold tuned post hoc); steps 1–3 are exploratory.
- tr_mmlu deepseek (+3.5pp) and mimo (+3.0pp) move ≥ +3pp but fail Holm — reported
  directional-only, never upgraded.

## License

MIT.
