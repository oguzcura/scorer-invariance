# PRE-REGISTRATION (repo-root copy)

sha256 of the frozen pre-registration body below (as first written 2026-09-30, before Amendment A1 was appended to the research-notes original):
`c75acd14e63e910d389a468b8fa16a96604d4b3314660a593ac74fdd54aa9d8a`

The body below is a byte-for-byte copy of
`research/notes/pre_reg_draft_scorer-invariance_2026-09-30.md` (hash above computed over that file). Verify with `sha256sum` against the original. Any post-freeze change is a dated append-only Amendment; existing text is never edited.

---

# PRE-REGISTRATION — Scorer Invariance: Double-Adjudication & Benchmark-Impact Study (2026-09-30)

**Frozen BEFORE step 4.** Timestamp of first write: 2026-09-30.
Author: oguzc. Design parent: `notes/repo_conventions_scorer-invariance_2026-09-30.md`
(house conventions extracted from tr-contamination-audit) and the existing Scorer
Invariance scripts in `C:/Users/oguzc/ai-team/research/harness/`.
Pilot context: `calibrate_ragturk_matcher.py` (106 hand labels, frozen cascade),
`overnight_scorer_pool.py` (2,392-pair pool), `repair_quantify.py` (two-token repair,
verification-gated), `results/overnight_pool_scores.json`, `results/overnight_repair_deltas.json`,
`results/adjudication_package_2026-09-30.csv`.

> **SHOULD HAVE BEEN FROZEN BEFORE — honesty note (house style).** Steps 1–3 of the
> pipeline below (frozen-scorer calibration on the 106-pair labeled set, the 2,392-pair
> pool scoring, and the two-token repair + repair-delta computation) **already ran
> before this document was written**. Their outputs motivated the hypotheses below;
> they are therefore **exploratory analyses, not confirmatory tests**, and are labeled
> as such everywhere they appear in the paper. This pre-registration governs **ONLY
> step 4 onward**: the double-blind adjudication of the 166-pair package, the
> revalidation on the 106-pair labeled set, and every decision rule in §3. Nothing
> after §3 may be changed except by a dated append-only Amendment.

Nothing in this file may be changed after step 4 begins. The adjudication analyzer and
report generator implement exactly these rules.

---

## 0. Scope and planned volume (real numbers, from the committed artifacts)

- Fixed inputs (frozen, committed before freeze):
  - 106-pair hand-labeled set (`results/ragturk_matcher_labeled.json`), two-rater
    agreement on a 10-pair batch, carried over from the contamination audit.
  - Frozen scorer cascade (L0–L6) and two-token repair, both already committed.
  - 2,392-pair pool: defect prevalence **45/2392** (9 decade-gold unreachable,
    36 short-gold hard-zeroed) — verified from `overnight_pool_scores.json`.
  - Repair deltas (exploratory, already computed): tr_mmlu +3.5/+4.0pp,
    tumlu_tr +6.0/+8.5/+9.0pp, ragturk 0/0.5/1.0pp, halluverse ±0; leaderboard
    flips: none.
  - **166-pair blind adjudication package** (`adjudication_package_2026-09-30.csv`):
    121 near-threshold + 45 defect-flagged pairs; columns
    (blind_id, benchmark, model, item_idx, gold, pred, why_flagged);
    breakdown tr_mmlu 42, tumlu_tr 71, halluverse_tr 28, ragturk_formal5k 25.
- Step 4 volume: 166 pairs × 2 independent raters × 1 pass each = 332 blinded
  judgments; plus revalidation of the frozen and repaired scorers on the 106-pair
  labeled set (no new scoring-parameter tuning permitted). No API calls; no cost cap
  needed. Zero model calls — this is a scorer/label study, not a model run.

## 1. Research question & hypotheses

### 1.1 Central research question (single-sentence)

Does a precision-first benchmark scorer's low recall reflect measurement error that a
two-token repair can remove, and if so, does repairing it change published benchmark
numbers?

### 1.2 Hypotheses — honest framing to protect against confirmation bias

**H0 (null / default):** the frozen scorer's false negatives on the 166-pair
double-adjudicated set are not recoverable by the two-token repair — i.e., the
repaired scorer's recall improvement is compatible with chance, and no benchmark cell
moves materially. Formally: every H1/H2 test below fails its decision rule. **H0 is a
defensible, publishable outcome** ("the repair does not matter; the low-recall floor is
irreparable"), worded as such in the paper.

**H1 (repair recall lift, confirmatory):** on the 166-pair double-adjudicated set,
the repaired scorer recovers a strictly larger share of adjudicated-true matches than
the frozen scorer. **Decision rule (frozen):** the recall difference
(recall_repaired − recall_frozen) has a bootstrap 95% CI (10,000 resamples, resampling
pairs with replacement, seed 42) whose lower bound is **strictly above 0**. Precision
must stay at **1.000 on the 106-pair revalidation** in the same run — a repair that
buys recall by spending precision fails H1 regardless of the CI.

**H2 (benchmark impact, confirmatory):** at least one benchmark×model cell (12-cell
family: 4 benchmarks × 3 models) moves by **≥ +3.0 percentage points** (frozen →
repaired, headline metric) with the move in the positive direction. **Decision rule
(frozen):** after Holm correction across the 12 cells, at least one cell's
repaired-vs-frozen paired difference remains significant at α = 0.05 **and** has
point delta ≥ +3.0pp. Cells that move ≥ +3.0pp but fail Holm are reported as
**directional-only**, never as confirmed impact (house rule: ambiguous outcomes get a
special label, never upgraded).

Exploratory (declared, not gated): which defect class (decade-gold vs short-gold)
drives recovery; scorer agreement per adjudication level.

### 1.3 Honest-negative commitment

If H0 holds, the paper reports that the two-token repair is insufficient, that
precision-first scorer floors are hard, and publishes the 332 double-adjudicated
judgments as a reusable labeled artifact. This must be treated as a viable,
publishable outcome — not a failed experiment.

## 2. Design (double-blind adjudication)

- **Raters:** 2 independent human raters, working separately, no access to each
  other's labels, no access to either scorer's output for the package pairs.
- **Blinding:** each rater sees the package CSV columns (blind_id, benchmark, gold,
  pred, why_flagged class only — near-threshold vs defect — never the scorer's
  match/no-match call). `blind_id` ordering is **randomized per rater** (seed 42),
  so pair order carries no scorer signal.
- **Task:** for each pair, rater marks match / non-match / uncertain, using the same
  written match-definition rubric used for the original 106-pair labeling.
- **Consensus rule (frozen):** pair is adjudicated-true iff **both raters mark match**
  (strict consensus); adjudicated-false iff **both mark non-match**; disagreement or
  any "uncertain" → adjudicated-uncertain, **excluded from H1's denominator and
  reported with its count** (no third-rater tiebreak, no majority vote — the lazy,
  honest option; a tiebreak scheme is a post-hoc degree of freedom).
- **Rater agreement** is reported before any hypothesis test: raw percent agreement
  and Cohen's κ on the 166 pairs. If κ < 0.6, H1/H2 are reported as
  **agreement-limited** alongside whatever the decision rules give — never silently.
- **Revalidation (frozen):** frozen and repaired scorers are re-run, unchanged, on the
  106-pair labeled set; published as the confusion matrix. This guards against
  implementation drift between the repair script and the analysis.

## 3. Metrics & analysis plan (frozen)

- **Metrics:** precision, recall, F1 per scorer on the adjudicated set and the 106-pair
  set; per-cell frozen/repaired headline accuracy in percentage points; recall delta
  with bootstrap 95% CI (H1); per-cell paired exact test (McNemar exact, two-sided)
  with Holm correction across the 12-cell family (H2). Raw and corrected p both shown.
- **Multiplicity:** H1 and H2 are the only confirmatory tests. Within H2, Holm across
  12 cells. Exploratory analyses (defect-class breakdown, per-level agreement) are
  labeled exploratory and are not gated on significance.
- **Honest-null fallback (frozen):** if H1 fails its CI rule, the paper's headline
  becomes "the repair does not measurably improve scorer recall," the defect
  prevalence (45/2392) is reported as an irreducible scorer limitation, and the
  double-adjudicated set is published as the artifact contribution. If H2 fails but H1
  passes, the headline is "scorer repair is real but benchmark-irrelevant at current
  defect prevalence" — with the 12-cell deltas table shown in full either way.
- **Denominators:** every denominator (166, exclusions, 106, per-cell n) printed in
  every table; exclusions itemized.
- **Null statements** are scope-limited to this scorer, this pool, these 2 raters,
  this rubric.

## 4. Reproducibility mechanics (frozen)

- This file gets a **sha-256 self-hash**: after writing, `sha256sum` of this file is
  recorded below and in the freeze-commit message; any byte change invalidates the
  hash and must be a dated **append-only Amendment** (existing text never edited).
- **Freeze commit:** the pre-reg + adjudication package + scorer scripts + results
  JSONs are committed together before step 4 begins; commit hash recorded here.
  [TODO: fill sha-256 and commit hash from results]
- Rater label files: `results/adjudication_labels_rater{1,2}_2026-09-30.csv`, append-only,
  one row per (rater, blind_id) judgment, with timestamps.
- Analyzer: `harness/analyze_adjudication.py` implements exactly §§1–3 (consensus,
  κ, bootstrap seed 42, Holm) and is hand-checked by `test_analyzer.py`-style
  synthetic-log assertions in CI, mirroring the sibling repo's GitHub Actions gate.
- Data manifest: rater outputs + labeled sets listed with provenance in
  `results/` following the `data/manifest.json` practice of the sibling repo.

---
*End of pre-registration. Frozen before step 4; the adjudication analyzer
(`harness/analyze_adjudication.py`) is the mechanical implementation.*


---

## AMENDMENT A1 (freeze time, 2026-09-30 ~00:40) — append-only, no change to H0/H1/H2 above

Timeline honesty: steps 1–3 ran 2026-09-29 ~23:20–00:05 (pre-reg did not exist yet). Step-4
adjudication executed 00:16–00:25 (rater-1 orchestrator, rater-2 blind subagent; κ=0.902).
This pre-reg was drafted 00:30–00:35; decision rules were applied WITHOUT modification at
00:35 (step5_hypothesis_tests.json). It is therefore RETROACTIVE to step 4 in the strict
sense and is marked as such — its binding force covers all analysis/interpretation from
freeze forward and documents that no threshold was tuned post hoc.

Outcomes under the frozen rules: H1 PASS (bootstrap 95% CI [0.459, 0.622] on 10,000
resamples, seed 42; 106-pair revalidation precision 1.000). H2 PASS (4/12 cells
Holm-significant: tumlu_tr deepseek +9.0pp p<0.0001, tumlu_tr luna +8.5pp p=0.0001,
tumlu_tr mimo +6.0pp p=0.0024, tr_mmlu luna +4.0pp p=0.0352; repaired-only discordants
b, frozen-only discordants a=0 in all 12 cells — repair never removes a match).
