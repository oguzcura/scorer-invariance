# DRAFT_TODO — morning list for scorer-invariance (written 2026-09-30 overnight)

Draft v0 is on disk at `paper/main_draft_v0.md` (all numbers traced to `results/`
artifacts; citations limited to the live-verified set in
`notes/verification_scorer_invariance_2026-09-30.md`). No git, no push, no LaTeX was
done overnight — everything below is morning work.

## 1. Verify the scaffold on disk (never trust the overnight self-report)
- [ ] `ls` the repo; confirm `pre-registration.md`, `paper/main_draft_v0.md`, 4 note
      files in `notes/`, 3 scripts in `harness/`, 11 files in `results/`.
- [ ] `sha256sum` the prereg body-copy against the research-notes original
      (header documents the expected value c75acd14…aa9d8a over the frozen body file).
- [ ] Spot-check 12-cell table in the draft against `results/step5_hypothesis_tests.json`
      + `results/overnight_repair_deltas.json` (the two JSONs agree exactly).

## 2. Git + GitHub
- [ ] `git init` in `C:/Users/oguzc/ai-team/coder/scorer-invariance`.
- [ ] `.gitignore` (paper PDFs, `__pycache__`, `.venv`), MIT `LICENSE` file, add
      `data/manifest.json` if dataset snapshots are copied (currently datasets are
      referenced in place under `research/harness/data/`; decide: copy 4 CSVs + manifest,
      or document paths — README/Reproducibility currently document paths).
- [ ] First commit referencing the prereg sha256 + freeze; create GitHub repo
      `oguzcura/scorer-invariance`, push. (House rule: no push without morning review.)

## 3. LaTeX conversion
- [ ] Convert `paper/main_draft_v0.md` → `paper/main.tex` (tectonic; TMLR style file;
      review option for double-blind when submitting).
- [ ] Transcribe Appendix A listings mechanically from
      `results/ragturk_matcher_labeled.json` (106 pairs) and the rater CSVs (166 pairs).
- [ ] Transcribe Appendix B L0–L6 definitions verbatim from the sibling audit's
      `notes/pre_reg_full_2026-08-16.md` + the calibration script docstring + by-level
      histogram from `ragturk_matcher_labeled.json`.
- [ ] References: replace bracketed short names with verbatim titles/authors (from the
      verification note), build `custom.bib`.

## 4. S6 bib-integrity audit pass
- [ ] Every BibTeX arXiv ID resolved live via arXiv export API; title verbatim-match
      (house claim-vs-verified table). Two items are abstract/title-level verified only
      (2607.02235, 2609.15467) — decide cite-or-drop based on full-text check.

## 5. CLAIM-CONF G0 sign-off request
- [ ] Ask Oğuz for G0 cost sign-off ($0.5–1.5) using `notes/claimconf_prep_2026-09-30.md`
      (research notes); also chase the OpenReview parental-consent email (gates TMLR lane).

## Open items inside the draft (marked in place)
- References list: bracketed short names pending verbatim titles (§References).
- Appendix A/B listings pending mechanical transcription (§Appendix).
