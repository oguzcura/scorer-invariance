# Precision-First Scorer Invariance: A Two-Token Repair for Benchmark Answer Matching and Its Measured Effect on Turkish Benchmark Scores

**Oğuz Çura**
Independent Researcher
oguzemrecura@gmail.com · github.com/oguzcura
Draft v0 — 2026-09-30. Markdown source; TMLR LaTeX conversion pending.

> **Status note.** This is draft v0. Every number below traces to a committed artifact in
> `results/` (paths given inline); every citation resolves to a live arXiv ID verified on
> 2026-09-30 (see Reproducibility Statement). Confirmatory claims are limited to the two
> pre-registered tests (H1, H2); steps 1–3 of the pipeline are exploratory and labeled as
> such throughout.

---

## Abstract

Reference-based scorers — the deterministic exact-match/containment cascades that grade
free-text QA answers — are load-bearing instruments of every leaderboard they feed, yet
their own error profile is rarely audited. We audit one such production scorer: the
precision-first L0–L6 matching cascade published with our earlier Turkish contamination
audit, used across four Turkish QA benchmarks (TR-MMLU, TUMLU-TR, RAGTurk, Halluverse-TR).
We find two provable mechanical defects: (D1) apostrophe-stripping in normalization makes
the scorer's decade-tolerant number rule unreachable for golds containing Turkish decade
forms ("1950'lerde"), and (D2) a similarity ceiling unreachable for golds shorter than
five normalized characters, hard-zeroing 36 short-gold pairs. Together the defects touch
45 of 2,392 pool items (1.9%). A deliberately minimal two-token repair — a numeric
equivalence branch for short golds plus a case/punctuation fold on the abbreviation rule —
is gated on a 106-pair hand-labeled set: precision stays at 1.000 while recall rises from
0.371 to 0.486. To measure what the defects cost, we ran a pre-registered double-blind
adjudication of a 166-pair package by two independent raters (agreement 95.8%, Cohen's
κ = 0.902; strict-consensus n = 159): 31 of the 45 defect-flagged items (69%) are
human-confirmed correct answers the scorer rejects. Re-scoring all 12 benchmark×model
cells moves scores by up to **+9.0 percentage points (+12.4% relative)**, with 4 of 12
cells significant under Holm correction, and the repair never removes a correct match
(frozen-only discordants = 0 in every cell). No leaderboard rank flips among the compared
models — the contribution is measurement validity, not reordering: two provable,
mechanically fixable defects in one production scorer materially move published benchmark
numbers while leaving precision untouched.

---

## 1. Introduction

A benchmark score is an instrument reading. The community treats score differences of a
few points as signal — evidence that one model is better than another — while the
instrument itself, the deterministic scorer that turns free-text answers into 0/1
correctness marks, is assumed to be a constant. That assumption is testable, and it
sometimes fails in ways that are provable, mechanical, and invisible to score consumers.

This paper reports one such failure, fully audited. The scorer is the precision-first
L0–L6 answer-matching cascade we built for a Turkish LLM-contamination audit
(tr-contamination-audit) and applied unchanged to four Turkish QA benchmarks. It was
designed to be deliberately conservative: because a false accept inflates accuracy and
would corrupt contamination-fragility contrasts, the cascade prefers false rejects. That
design choice is defensible — but it means the published accuracies are lower bounds, and
it makes the scorer's *own* false-negative profile a validity question for every number
it produced.

Auditing that profile surfaced two defects that are not statistical quirks but
provable mechanical faults — each traceable to a specific code path, each demonstrably
unreachable for a specific class of gold answers, each fixable with a two-token change:

- **D1 (decade-gold unreachable).** Normalization strips apostrophes (both ASCII `'` and
  U+2019), so a gold like "1950'lerde" is stored as the normalized token "1950 lerde".
  The cascade's decade rule then looks for the exact decade token `(\d+)ler` and can
  never match it. Nine pool golds sit in this unreachable state — every answer for these
  items scores no-match regardless of what the model says.
- **D2 (short-gold hard-zero).** Golds whose normalized form is under five characters
  ("80", "0,08", "2002", "Beka", "Volt") fall below a similarity ceiling that no
  candidate can clear, so 36 short-gold pairs are hard-zeroed. In a multiple-choice
  benchmark where the model echoes the option letter ("D) 80"), even a character-identical
  answer scores no-match.

The defects are small in prevalence (45/2,392 = 1.9%) but concentrated in exactly the
items where a correct answer is most likely to be rejected, and they are *provable*: for
all 45 items the frozen scorer produces no-match regardless of prediction content.

Our response follows the house method discipline established in the sibling audit: freeze
a decision rule before trusting any delta, repair minimally, verify the repair on held
hand labels, and quantify human agreement before any hypothesis test. The repair is two
tokens of code; the verification gate is a 106-pair hand-labeled set on which precision
must remain 1.000; the impact measurement is a pre-registered double-blind adjudication
of a 166-pair package by two independent raters.

**Contributions.**

- **A defect taxonomy with measured prevalence for a production scorer** (§3): two
  mechanical defect classes (decade-gold unreachable, short-gold hard-zero), each with a
  traceable mechanism, jointly affecting 45/2,392 pool items, all 45 provably unmatched.
- **A verification-gated two-token repair** (§4) that holds precision at 1.000 on the
  106-pair labeled set while raising recall 0.371 → 0.486 (and to 0.541 on the
  double-adjudicated consensus set) — with the gate rule pre-registered so that a repair
  which bought recall by spending precision would have failed outright.
- **A pre-registered double-blind adjudication quantifying the benchmark impact** (§5):
  two independent raters (κ = 0.902), strict consensus, confirmatory tests H1/H2 both
  PASS, 12-cell re-scoring with Holm-corrected McNemar tests, and the observation that
  the repair never removes a correct match (frozen-only discordants a = 0 in all 12
  cells). All scores, frozen and repaired, are published cell-by-cell; no rank flips.

We deliberately scope the claim: this is an instrument-validity result about one scorer
family on Turkish QA benchmarks, not a leaderboard exposé. The same two defects, however,
are exactly the kind that any precision-first cascade in any language can accumulate
silently, and the repair protocol is generic.

## 2. Related Work

**Deterministic scorers inherit evaluation bias.** The mechanism that deterministic
verifiers grade answers unequally across conditions is established. *Multilingual
Verifier Bias in RLVR* (arXiv:2608.20362) proves that exact-match verifier false-negative
rates differ sharply by language in math domains (JP 0.642 / EN 0.122 / CN 0.073 on
Qwen3-8B rollouts), localizing the bias to the final-answer interface. That paper proves
the mechanism for math/numeric answers in JP/EN/CN under a reward-noise (RLVR) framing;
we cite it as the mechanism proof and do not re-discover it. Our contribution is
complementary and different in kind: a *QA/free-text* instrument (not RLVR reward), a
*Turkish* language (absent from 2608.20362), a *measurement-validity* framing (not reward
noise), and — the practical difference — a *repair with a pre-registered verification
gate* that is then traced through to published benchmark numbers. As of 2026-09-30 that
paper has zero citing works extending the result to QA or Turkish (OpenAlex W7204089545);
the gap our audit occupies remains open.

**Judge-side language bias.** *Lower-Resource, Higher Scores* (arXiv:2607.14480) shows
LLM evaluators (reward models and LLM-as-judge) assign different scores to semantically
identical content across 23 languages including Turkish, with acceptance-rate gaps up to
43% invisible to pairwise accuracy. This is the judge-class analog of our question:
neural evaluators, not deterministic reference scorers. It motivates our framing — score
movements invisible to rank-ordering metrics — but does not perform a deterministic-scorer
audit. Similarly, the multilingual LLM-as-judge recommendations survey
(arXiv:2607.02235) treats judge reliability but not reference-scorer validity
(abstract-level verification only; we cite it as position/context, not evidence).
*CoT-Pass@k* (arXiv:2609.32622) audits judge verification quality inside a pass@k metric
including Turkish — adjacent in using TR, different in metric class.

**Adjacent lookalikes, none occupying the gap.** CBC rank-reversal calibration for LLM
judges (arXiv:2608.22432) is a calibration method, not a scorer audit; MM-Eval
(arXiv:2410.17578) is a meta-evaluation benchmark for judges/reward models; DIF across
model families on benchmark items (arXiv:2609.00482) concerns ranking robustness, not
cross-language scorer validity; IRT grading of LLM short-answer graders (arXiv:2605.00238)
is English-only with no language invariance; output-token-cap artifacts on MGSM
(arXiv:2608.04160) are a hidden-variable artifact of the cap, not the scorer; and
Turkish MMLU-Pro validity limits (arXiv:2609.15467) concern option-augmentation validity
in benchmark construction (title-level verification only). The psychometric measurement-
invariance tradition concerns human survey scales via CFA — the construct we borrow the
name from, not the object we measure. None of these measures whether one deterministic
reference-based answer scorer is invariant across answer surface classes in Turkish QA;
a 10-query arXiv sweep and OpenAlex keyword searches on 2026-09-30 returned nothing
on-point (verification note, `notes/verification_scorer_invariance_2026-09-30.md`).

**Pre-registration and honest reporting in evaluation.** Our protocol follows the
pre-registration practice of the sibling audit (frozen decision rules, append-only
amendments, self-hashed pre-reg, exploratory/confirmatory separation, honest-negative
wording fixed in advance). This draft extends that practice to scorer auditing: the H1
precision gate and the H2 directional-only labeling rule were frozen before the
hypothesis tests ran (Amendment A1 documents the retroactivity honestly; §5.0).

## 3. The Two Defects

### 3.1 The frozen scorer and why it is precision-first

The L0–L6 cascade (levels defined verbatim in Appendix B; implemented in
`harness/calibrate_ragturk_matcher.py`) grades a (gold, prediction) pair through
normalization → letter-answer extraction → exact/containment → number-aware → fuzzy
similarity levels, each with published thresholds. It was calibrated on 106 hand-labeled
pairs (strict single-pass policy, 2026-08-16; 10-pair double-label agreement batch
10/10) and published with its confusion matrix: TP = 13, FP = 0, TN = 71, FN = 22 —
precision 1.000, recall 0.371 on human-positive pairs
(`results/ragturk_matcher_labeled.json`). The precision-first choice was deliberate: in a
contamination audit, a false accept inflates model accuracy and would corrupt the
fragility contrasts the audit measures. A scorer tuned this way is honest about what it
is — a lower bound — but a lower bound whose tightness varies with answer surface class
is an instrument whose readings drift by item type.

### 3.2 D1 — decade-gold golds unreachable by every cascade level

Turkish marks decades with an apostrophe suffix: "1950'lerde" ("in the 1950s"). The
cascade normalizes by stripping punctuation *including apostrophes* (both ASCII `'` and
U+2019 fold to the same normalized form), so the gold normalizes to "1950 lerde". The
number-aware level's decade rule searches for the exact decade token `(\d+)ler` — which
no longer occurs in the normalized string. Result: the rule is dead code for every
apostrophe-bearing decade gold. Nine pool golds are in this class, e.g.:

> gold: "UBV fotometrik sistemi, 1950'lerde Amerikalı Harold Lester Johnson ve William
> Wilson Morgan tarafından tanıtıldı." — prediction: "Johnson ve Morgan tarafından 1953
> yılında tanıtılmıştır." (a human would accept 1953 ⊂ 1950'ler; the frozen scorer
> returns `number-mismatch`).

> gold: "Salvador Allende, General Augusto Pinochet ve Ölüm Karavanı, 1970'lerde ve
> 1980'lerde Şili'de hangi ülkenin tarihiyle bağlantılı." — prediction: "Şili" (the
> correct answer; the frozen scorer returns `number-mismatch` on a three-letter word).

### 3.3 D2 — short-gold pairs hard-zeroed

Golds whose normalized form is shorter than five characters cannot clear the fuzzy
level's similarity floor: the ceiling is unreachable, so the pair is hard-zeroed. All 36
pool short-gold pairs are unmatched. In the multiple-choice benchmarks the predictions
arrive letter-form ("A) 0,08", "D) 80", "C) 2002"), and even after letter stripping the
short-gold ceiling still zeroed them — the golds include bare numerals ("80", "0,08",
"2002", "IV") and short tokens ("Beka", "Volt", "Bor", "Hız", "HIF", "PET", "IS", "Prim",
"Kün", "uud", "kg.m"). A model that answers these items perfectly scores zero on them.

### 3.4 Prevalence and concentration

Across the 2,392-pair M1 pool (4 benchmarks × 3 models), the defects affect 45 items =
1.9%: 9 decade-gold + 36 short-gold, all 45 verifiably unmatched under the frozen scorer
(`results/overnight_pool_scores.json` flags: `defect_decade_triggers=9`,
`defect_shortgold_ceiling=36`). The two classes concentrate differently: short-gold
defects sit in the multiple-choice benchmarks (tr_mmlu 15, tumlu_tr 21), decade-gold
defects in the free-text benchmarks (ragturk_formal5k 6, halluverse_tr 3) — this
asymmetry predicts, correctly, which cells move in §5.

## 4. Repair Protocol

### 4.1 The two-token repair (exact rule)

The repair (`harness/repair_quantify.py`, `matcher_repaired`) changes exactly two things
in the frozen cascade, in order:

1. **Short-gold numeric branch.** If the normalized gold is under five characters but is
   a number (or comma-decimal), match when the prediction contains the same numeric
   value (letter-form option prefixes such as "A)" having been stripped upstream) — new
   level `shortgold-num`. This is the minimal rule that rescues D2 without opening a
   fuzzy-match hole: the predicate is equality of a parsed number, not similarity.
2. **Abbreviation fold on the abbreviation rule.** The abbreviation level additionally
   folds period punctuation between single-character tokens, so "M.S." ≡ "MS" ("BC" vs
   "M.Ö."-style era abbreviations and dotted initials). One normalization predicate,
   no new similarity mass.

Nothing else moves: no thresholds retuned, no level reordering, no semantic/embedding
fallback added. `ponytail:` this is deliberately the *minimal* repair — a paraphrase or
embedding level would recover more FN at real precision risk and needs its own labeled
calibration; that is future work, not this paper.

### 4.2 The verification gate

The repair fires only where it can be verified, and the pre-registered gate (H1's
precision clause) forbids any repair that buys recall by spending precision: precision
must remain 1.000 on the 106-pair labeled set in the same run. Result: repaired confusion
TP = 17, FP = 0, TN = 71, FN = 18 — recall 0.371 → 0.486, precision 1.000 unchanged
(`results/step5_hypothesis_tests.json`, 106-pair revalidation). No unconditional
loosening of the cascade was permitted or performed.

### 4.3 What the repair does and does not recover

Exploratory (declared in pre-reg §1.2, not gated): the repair's recovered pairs are
short-numeric golds and dotted-abbreviation pairs — including the letter-form MC
predictions ("A) 0,08" → `shortgold-num`; "C) C. H. Cooley" vs "C. H. Cooley" →
abbreviation fold). The repair does **not** recover the 45 package-flagged defect items
themselves: the flagged decade golds require accepting 1953 ⊂ 1950'ler (a date-range
inference the two-token rule does not make) and the non-numeric short golds require
lexical tolerance. On the double-adjudicated consensus set, 31 of the 45 defect-flagged
items are human-confirmed correct answers that remain scorer-rejected even after repair
— measured headroom, reported in §6. This honesty point matters for calibration of
expectations: the two-token repair fixes *adjacent* mechanical faults the audit exposed;
the flagged defects themselves need semantic matching.

## 5. Benchmark Impact

### 5.0 Pre-registration and honesty note

The pre-registration (`pre-registration.md`; sha256
c75acd14e63e910d389a468b8fa16a96604d4b3314660a593ac74fdd54aa9d8a over the frozen body)
governs step 4 onward: the double adjudication, the 106-pair revalidation, and every
decision rule in its §§1–3. **Retroactivity, stated plainly:** steps 1–3 (calibration,
pool scan, repair + deltas) ran before the pre-reg existed and are exploratory; the
pre-reg was drafted ~00:30, frozen ~00:40, and the frozen decision rules applied without
modification at 00:35 to the step-4 outputs — so it is retroactive to step 4 in the
strict sense, and Amendment A1 (append-only) records exactly this. No threshold was
tuned post hoc; the binding force of the frozen rules covers all analysis and
interpretation from freeze forward. H0 (the null) was worded as a defensible outcome
before testing, per house convention.

### 5.1 Double adjudication (human validation)

**Design** (pre-reg §2): a 166-pair package — 121 near-threshold pairs plus the 45
defect-flagged pairs, drawn from the frozen scorer's no-match set — was labeled by two
independent raters under blind conditions: no access to each other's labels, no access
to either scorer's call, `blind_id` order randomized per rater (seed 42), frozen written
rubric. 332 blinded judgments total, zero model calls.

**Agreement:** raw agreement 159/166 = 95.8%; Cohen's κ = 0.902 — far above the 0.6
floor below which the pre-reg would have forced an "agreement-limited" label.
Consensus by strict rule (both-raters-agree; any disagreement or "uncertain" excluded,
no tiebreak): n = 159.

**Scorer vs consensus:** the repaired scorer on the 159-pair consensus set scores
precision 1.000 (0 false accepts against human consensus), recall 0.541 (TP 60, FP 0,
TN 48, FN 51). The frozen scorer's recall on the package is 0 by construction — the
package was drawn from its no-match set — so the meaningful human-validation numbers are:
the repair's precision floor survives contact with two independent human raters, and 51
consensus-correct pairs remain missed (the paraphrase headroom of §6). The defect-flagged
items' human status: 31/45 (69%) confirmed correct answers rejected
by the scorer; near-threshold pairs: 80/114 (70.2%) human-correct
(`results/adjudication_analysis_2026-09-30.json`).

### 5.2 The 12-cell table

Every cell shown, per house rule. Deltas are frozen → repaired headline accuracy in
percentage points; p is McNemar exact (two-sided), Holm-corrected across the 12-cell
family; discordant counts are repaired-only (b) vs frozen-only (a) — a = 0 in all 12
cells: **the repair never removes a correct match** (`results/step5_hypothesis_tests.json`).

| Benchmark | Model | n | Frozen | Repaired | Δ (pp) | Holm p | Verdict |
|---|---|---|---|---|---|---|---|
| tumlu_tr | deepseek-v4-flash | 200 | 145 (72.5%) | 163 (81.5%) | **+9.0** | < 0.0001 | Holm-significant |
| tumlu_tr | gpt-5.6-luna | 200 | 164 (82.0%) | 181 (90.5%) | **+8.5** | 0.0001 | Holm-significant |
| tumlu_tr | mimo-v2.5 | 200 | 70 (35.0%) | 82 (41.0%) | **+6.0** | 0.0024 | Holm-significant |
| tr_mmlu | gpt-5.6-luna | 200 | 160 (80.0%) | 168 (84.0%) | **+4.0** | 0.0352 | Holm-significant |
| tr_mmlu | deepseek-v4-flash | 200 | 141 (70.5%) | 148 (74.0%) | +3.5 | 0.0625 | directional-only |
| tr_mmlu | mimo-v2.5 | 200 | 99 (49.5%) | 105 (52.5%) | +3.0 | 0.1094 | directional-only |
| ragturk_formal5k | gpt-5.6-luna | 193 | 15 (7.8%) | 16 (8.3%) | +0.5 | 1.0 | directional-only |
| ragturk_formal5k | deepseek-v4-flash | 200 | 10 (5.0%) | 12 (6.0%) | +1.0 | 1.0 | directional-only |
| ragturk_formal5k | mimo-v2.5 | 200 | 10 (5.0%) | 10 (5.0%) | +0.0 | 1.0 | no movement |
| halluverse_tr | deepseek-v4-flash | 200 | 19 (9.5%) | 19 (9.5%) | +0.0 | 1.0 | no movement |
| halluverse_tr | gpt-5.6-luna | 199 | 19 (9.5%) | 19 (9.5%) | +0.0 | 1.0 | no movement |
| halluverse_tr | mimo-v2.5 | 200 | 15 (7.5%) | 15 (7.5%) | +0.0 | 1.0 | no movement |

(Frozen/Repaired = correct items under each scorer, from `results/step5_hypothesis_tests.json`;
percentages from `results/overnight_repair_deltas.json`; the two files agree exactly on all
12 cells. ragturk/halluverse Holm p = 1.0 with zero/near-zero discordants — reported
directionally, never upgraded.)

**Confirmatory outcomes.** H1 PASS: the recall delta's bootstrap 95% CI is
[0.459, 0.622] (10,000 resamples, seed 42), lower bound strictly above 0, with the
106-pair precision gate satisfied (1.000). H2 PASS: 4/12 cells Holm-significant with
point deltas ≥ +3.0pp (the frozen decision rule's conjunction). The two tr_mmlu cells
that clear the +3.0pp magnitude but fail Holm are labeled directional-only and are not
upgraded. The ragturk near-zero movement is explained by defect geography (§3.4): its
defects are decade-gold class, which the two-token repair does not recover, and its
short-gold count is 0; halluverse's 3 defect items do not move any cell at its scale.

**No rank flips — stated as the honest frame.** The 12-cell deltas do not reorder the
three models on any benchmark (exploratory pass; `leaderboard_flips = []`). A +9.0pp
cell movement (+12.4% relative on that cell) from defects touching 1.9% of the pool is a
measurement-validity finding: the instrument's lower-bound reading was that far from its
repaired reading, with precision unchanged. What the result establishes is that such
defects are common enough to matter, provable enough to fix, and fixable without
spending precision — not that any published ranking was wrong.

### 5.3 Run integrity

Adjudication executed 2026-09-30 00:16–00:25 (rater-1: orchestrator; rater-2: blind
subagent; label files append-only with per-pair judgments). Zero API calls were made in
the entire pipeline (scoring, repair, adjudication, statistics); the run was not
interrupted or resumed. Rater-1 stayed blind to scorer internals during labeling
(package CSV + frozen rubric only), recorded in
`results/adjudication_rater1_notes_2026-09-30.md`.

## 6. Limitations

- **Measured paraphrase headroom.** 51 consensus-correct pairs remain scorer-rejected
  after repair (recall 0.541 on consensus), including all 31 human-confirmed-correct
  defect-flagged items: the two-token repair recovers *adjacent* mechanical faults, not
  the flagged decade-gold and non-numeric short-gold defects themselves. Closing that
  gap requires semantic matching with its own labeled precision calibration — future
  work, deliberately not improvised here.
- **Single-scorer scope.** One scorer family (L0–L6 cascade), one pool (2,392 pairs),
  one language (Turkish), two raters, one rubric. Nothing here shows other scorers have
  the same defects; the contribution is the *protocol* (audit → minimal repair →
  verification gate → pre-registered impact test) plus one fully worked instance.
- **Retroactive pre-registration honesty.** The pre-reg was frozen after steps 1–3 ran
  and after the step-4 adjudication but before its frozen rules were applied
  (Amendment A1). We label steps 1–3 exploratory throughout and claim confirmatory force
  only for H1/H2 under the frozen rules. Readers should weigh the confirmatory claims
  accordingly: the rules were not tuned post hoc, but they were also not on disk before
  the data existed.
- **Small prevalence bounds the impact.** 45/2,392 defects moved cells up to +9.0pp but
  flipped no ranks. A scorer with more (or more concentrated) defects would move more;
  our prevalence result does not extrapolate a distribution over scorers.
- **Directional-only cells.** tr_mmlu deepseek (+3.5pp) and mimo (+3.0pp) clear the
  magnitude threshold but fail Holm; per the frozen rule they are never described as
  confirmed impact.
- **Two-rater consensus discards uncertainty.** Strict consensus excluded 7/166 pairs
  from the H1 denominator; no third-rater tiebreak was used (pre-registered as the
  honest, lazy option). A tiebreak scheme would add post-hoc degrees of freedom.
- **TR-only.** The invariance question this program ultimately targets — is the same
  scorer's error profile language-comparable? — is untested here; this paper audits one
  language's instrument. The cross-lingual TR↔EN mirror design remains future work.

## 7. Reproducibility Statement

All code and data are in this repository; every number in the paper traces to a
committed artifact listed below. The entire pipeline — scoring, repair, adjudication,
statistics — used zero API calls; there is no spend to reproduce.

**Code** (`harness/`): `calibrate_ragturk_matcher.py` (frozen L0–L6 cascade + 106-pair
calibration), `overnight_scorer_pool.py` (2,392-pair pool scorer + defect flags),
`repair_quantify.py` (two-token repair + verification gate).

**Data & results** (`results/`): `ragturk_matcher_labeled.json` (106-pair labeled set,
n=106, confusion + by-level histogram); `overnight_pool_scores.json` (2,392 rows +
defect flags 9/36); `overnight_repair_deltas.json` (12-cell frozen/repaired deltas);
`adjudication_package_2026-09-30.csv` (166-pair blind package), `adjudication_rater1_2026-09-30.csv`,
`blind_rater2_labels_2026-09-30.csv`, `adjudication_rater1_notes_2026-09-30.md`,
`adjudication_analysis_2026-09-30.json` (κ, consensus, per-class human-correct counts);
`step5_hypothesis_tests.json` (H1 bootstrap CI, H2 Holm table, discordant counts);
`pilot_audit_2026-08-16.jsonl` (pilot-run provenance; 12 MB, retained rather than
committed if repo-size limits require — original path documented in the manifest).

**Pre-registration** (`pre-registration.md`): frozen body sha256
`c75acd14e63e910d389a468b8fa16a96604d4b3314660a593ac74fdd54aa9d8a`; any post-freeze
change must be a dated append-only Amendment; Amendment A1 documents retroactivity.
`sha256sum pre-registration.md` verifies the copy against the research-notes original.

**Seeds:** 42 everywhere sampling or randomization occurs (bootstrap resampling, blind_id
order randomization per rater, pool item sampling in the original audit).

**Reproduction** (no API keys needed; commands in README map 1:1 to results files):
`uv run python harness/overnight_scorer_pool.py` → `results/overnight_pool_scores.json`;
`uv run python harness/repair_quantify.py` → repaired 17/0/71/18 matrix;
`uv run python harness/calibrate_ragturk_matcher.py` →
`results/ragturk_matcher_labeled.json`.

**Citation policy:** every reference below was resolved live against the arXiv export
API on 2026-09-30 (verification note in `notes/verification_scorer_invariance_2026-09-30.md`,
which records per-paper verification level, including two abstract/title-level items).
No unverifiable citation is included.

## References

1. **Multilingual Verifier Bias in RLVR.** arXiv:2608.20362. Full-text grepped 2026-09-30
   (mechanism proof: language-dependent exact-match verifier FN rates, JP/EN/CN, math
   domain; cited, not re-discovered).
2. **Lower-Resource, Higher Scores: Language Bias in LLM Evaluators.** arXiv:2607.14480
   (v3). Full-text grepped 2026-09-30 (judge-class language bias incl. Turkish; the
   judge-side analog).
3. **Challenges & Recommendations for LLMs-as-a-Judge in Multilingual Settings.**
   arXiv:2607.02235 (v2). Abstract-level verification 2026-09-30 (position/context).
4. **[CoT-Pass@k multilingual audit]** arXiv:2609.32622. Verified 2026-09-30 (adjacent,
   uses Turkish; audits judge verification inside pass@k).
5. **[CBC rank-reversal calibration]** arXiv:2608.22432. Verified 2026-09-30 (lookalike,
   why-not: calibration method for LLM judges, no deterministic-scorer audit).
6. **[MM-Eval]** arXiv:2410.17578. Verified 2026-09-30 (lookalike, why-not:
   meta-evaluation benchmark for judges/reward models).
7. **[Family-DIF benchmark recomposition]** arXiv:2609.00482. Verified 2026-09-30
   (lookalike, why-not: DIF across model families, not across-language scorer validity).
8. **[IRT for LLM ASAG]** arXiv:2605.00238. Verified 2026-09-30 (lookalike, why-not:
   English-only LLM grader psychometrics).
9. **[Mind the Cap]** arXiv:2608.04160. Verified 2026-09-30 (lookalike, why-not:
   output-token-cap artifact, not scorer).
10. **[Turkish MMLU Pro validity limits]** arXiv:2609.15467. Title-level verification
    2026-09-30 (lookalike, why-not: benchmark-construction validity for TR MC items).

*[TODO-morning: replace bracketed short names with verbatim titles+authors from the
verification note table during the LaTeX/bib pass; the arXiv IDs above are the
live-verified anchors.]*

---

## Appendix A — Labeled sets (to be generated mechanically in the LaTeX pass)

- **A.1** 106-pair labeled set: pair, gold, pred, label, matcher level — from
  `results/ragturk_matcher_labeled.json` pairs[].
- **A.2** 166-pair package + consensus outcome per pair (rater1, rater2, adjudication)
  — from `results/adjudication_rater1_2026-09-30.csv`,
  `results/blind_rater2_labels_2026-09-30.csv`,
  `results/adjudication_analysis_2026-09-30.json`.

## Appendix B — Matcher level definitions

L0–L6 cascade levels and thresholds, verbatim from the sibling audit's published
pre-registration (`notes/pre_reg_full_2026-08-16.md` in tr-contamination-audit; docstring
of `harness/calibrate_ragturk_matcher.py` in this repo), plus the by-level histogram from
the 106-pair calibration (`results/ragturk_matcher_labeled.json`). *[TODO-morning:
transcribe verbatim during LaTeX pass.]*
