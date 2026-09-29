# Verification note — "Scorer Invariance" gap — 2026-09-30 (overnight, live-checked)

**Claim audited:** *"Does one reference-based (deterministic) answer scorer measure the same thing in Turkish
and in English?"* — i.e. a measurement-invariance audit of a single reference-based scorer (exact match /
containment / numeric-normalization cascade) on QA answers, stratifying its false negatives by answer surface
type, and whether scorer error is language-comparable on leaderboards. (Origin: `notes/ideas/deepdive_2026-09-20.md`.)

**Method:** skill `research-novelty-verification` checks 1–3, all free sources: arXiv export API
(11 IDs resolved live, 10 query sweeps), full-text greps of the two strongest threats via ar5iv, OpenAlex
(mailto oguzemrecura@gmail.com) citation + keyword search, web_search. Local repo data inspected.
All arXiv IDs below resolved on https://export.arxiv.org (id_list) on 2026-09-30 unless marked otherwise.

---

## 1. Claims verified (paper | what was checked | verdict)

| Paper | What was checked | Verdict |
|---|---|---|
| **2608.20362** *Multilingual Verifier Bias in RLVR* (v1, 2026-06-17) | Full text (ar5iv) grepped: `exact match`×8, `false negativ`×6, `Turkish`×0, `short answer`×0, `stratif`×0, `wrapper`×2, `normaliz`×10. Own experiments = JP/EN/CN MGSM + MATH-500 rollouts; stress suite covers currency symbols, full-width digits, CJK units. | **Live threat to the mechanism claim, not to the gap**: exact-match verifier FN rate differs sharply by language (Qwen3-8B: JP 0.642 / EN 0.122 / CN 0.073; VLB 0.569), localized to the final-answer interface. But domain = math/numeric answers; languages JP/EN/CN, **no Turkish**; framing = RLVR reward noise, not benchmark/leaderboard measurement validity; no free-text QA; "scorer invariance" as a construct never named or measured. |
| **2607.14480** *Lower-Resource, Higher Scores: Language Bias in LLM Evaluators* (v3, 2026-07-16) | Full text (ar5iv) grepped: `Turkish`×4 (only in the 23-language table; tr scored), uncertainty analysis, threshold/acceptance-rate analysis. | LLM evaluators (reward models + LLM-as-judge) assign different scores to semantically identical content across 23 languages incl. Turkish; up to 43% acceptance-rate gap invisible to pairwise accuracy. **Judge-class evidence, not deterministic-scorer evidence** — supports our motivation, does not occupy the gap. |
| OpenAlex **W7204089545** (= 2608.20362) | `cites:W7204089545` | **0 citing works** as of 2026-09-30 → no fast-follower has extended the multilingual-verifier result into QA/Turkish. Race not on (yet). |
| OpenAlex keyword searches (`scorer invariance`; `exact match multilingual bias`; `answer matching multilingual evaluation validity`) | title_and_abstract.search, sorted desc | Nothing on-point: no paper measures cross-lingual invariance of deterministic reference-based answer scorers. Hits are unrelated (OCR, retrieval, health-advice eval). |
| **2607.02235** *Challenges & Recommendations for LLMs-as-a-Judge in Multilingual Settings/LRLs* (v2, 2026-09-07) | Abstract + secondary reporting (aiweekly.co) via web_search; **full-text grep NOT run** | Position/survey paper (650-paper scope, 33 multilingual/LRL). No measurement of deterministic scorers. [Abstract-level verified only.] |
| arXiv sweeps (10 queries: verifier+multilingual, answer verification+multilingual, Turkish+evaluation, Turkish+metric, reward+multilingual+false negative, exact match+verifier, scorer+language, benchmark validity+language, DIF+language, judge+Turkish; sortBy=submittedDate desc) | titles of last ~3–12 months | No paper titled or claiming scorer/metric invariance across languages for reference-based QA scoring. |
| Local evidence `research/harness/results/ragturk_matcher_labeled.json` | Re-loaded this session: n=106 (M2b_A/M2b_B probes), confusion tp=13, fp=0, tn=71, **fn=22** → recall on human-positive pairs = 13/35 ≈ **0.371**; FN classes = `M.S.` vs `MS` (abbreviation dots), markdown-wrapped verbose answers, date paraphrase ("1950'lerde" vs "1953 yılında"). | Motivating artifact is real and re-verified; the invariance question (same scorer, TR vs EN comparability) is untested in-repo. |

## 2. Surviving gap, restated (falsifiable)

**The gap would be CLOSED if** there existed a published measurement-invariance audit of a deterministic
reference-based answer scorer showing whether its error profile (false-negative rate stratified by answer
surface class: numeric+unit, year/date, abbreviation punctuation, wrapped/verbose correct answers, lexical
variants) is language-comparable — same items, TR↔EN — on a QA leaderboard/instrument, with the scorer-invariance
construct named and quantified. **As of 2026-09-30 no such paper exists** in arXiv (full-text checks of the two
strongest candidates + 10 query sweeps), OpenAlex, or the open web. The mechanism (language-dependent
deterministic-scorer error) is proven for **math/numeric answers in JP/EN/CN under RLVR** (2608.20362); the
**QA / Turkish / leaderboard-instrument** instantiation is unoccupied.

Verdict: **PARTIALLY_OPEN** — the headline mechanism is taken (cite it, don't re-discover it); the QA/free-text/
Turkish measurement-invariance audit, and the leaderboard-validity framing, remain open and are now *more*
motivated by 2608.20362 + 2607.14480.

## 3. Lookalike triage (paper | why-not-the-gap)

| Paper | Why it is not the gap |
|---|---|
| 2608.20362 (Multilingual Verifier Bias in RLVR) | Math numeric answers, JP/EN/CN, RLVR reward-noise framing; no Turkish, no free-text QA, no leaderboard-measurement framing; "invariance" never a construct. |
| 2607.14480 (Language Bias in LLM Evaluators) | Neural evaluators (reward models/judges), not deterministic reference scorers; shows pairwise accuracy masks bias — motivates ours, doesn't do it. |
| 2608.22432 (CBC rank-reversal calibrator) | Recovers judge-score language interactions by double-centering for LLM judges; calibration method, no deterministic-scorer audit. |
| 2410.17578 (MM-Eval) | Meta-evaluation *benchmark* for judges/reward models incl. score fairness; resource, not an invariance audit of matchers. |
| 2609.32622 (CoT-Pass@k multilingual audit, incl. TR) | Audits judge verification quality inside a pass@k metric; not reference-scorer language comparability. Adjacent (uses TR) — cite. |
| 2609.00482 (Family-DIF benchmark recomposition) | DIF across **model families** on benchmark items; ranking robustness, not across-language scorer validity. |
| 2605.00238 (IRT for LLM ASAG) | LLM grader ability/difficulty via IRT; English SciEntsBank/Beetle only; no language invariance. |
| 2608.04160 (Mind the Cap) | Output-token budget as hidden variable on MGSM; measurement artifact of the cap, not the scorer. |
| 2607.02235 (LLM-judge multilingual survey) | Recommendations/position paper on judge reliability; no scorer measurement. [Abstract-level only.] |
| 2609.15467 (Turkish MMLU Pro validity limits) | TR benchmark construction (option augmentation validity); multiple-choice, not answer-scorer invariance. [Title-level only.] |
| Raschka FAQ "exact match vs LLM-judge" (sebastianraschka.com) | Practitioner guidance: EM brittle when surface form varies — folklore-level, no cross-lingual measurement. |
| Psychometric "measurement invariance" literature (e.g. Turkish scale validations) | Human survey-scale invariance via CFA; not LLM answer scoring. |

## 4. Next actions

1. **Fast first pass (no API spend):** run `research/scratch/dsf_precheck_2026-09-20.py` on the 106 labeled
   pairs to get the FN stratification table; then the paired TR/EN scorer-invariance experiment on the frozen
   cascade + one EN mirror set. Power table already computed in the precheck (e.g. recall .371→.70 needs
   n≈24/stratum; .65→.80 needs n≈148/stratum — recompute exactly at run time).
2. **Related-work positioning:** cite 2608.20362 as the RLVR-side proof of the mechanism and 2607.14480 as the
   judge-side analog; claim only the QA/free-text/Turkish instrument audit as novel.
3. **Monitor:** OpenAlex citation alert on W7204089545 (0 citations today); re-run the 10-query sweep monthly;
   re-check `cites:` before any write-up submission.

## Pitfalls honored
- Full texts of both top threats grepped this session (not abstracts, not memory).
- Fast-follower sweep = OpenAlex citing-works (0) + submittedDate-desc sweeps (empty for the gap).
- Every lookalike has an explicit why-not line; unverifiable-at-level items marked.
