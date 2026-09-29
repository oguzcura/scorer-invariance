# Rater-1 (orchestrator) adjudication notes — 2026-09-30

- Labels: 118 × 1, 48 × 0, n=166. File: adjudication_rater1_2026-09-30.csv (sha256[:16]=7112ba8751bab47a)
- Policy application notes (for disagreement analysis):
  - Explicit correct content stated mid-response (even if formatting is messy) counts 1 (e.g. Q060 'A) Cisim...', Q103 'So answer D', Q127 quoting the correct source sentence).
  - Hedged/uncertain ('probably', 'Need exact') or trailing off with NO correct content stated counts 0 (e.g. Q067, Q149).
  - Entity substitutions that change the referent count 0 (Q142 'Berlin Duvarı Anıtı' vs 'Berlin Duvarı'; Q147 'Yeni bir el' vs 'Protez bir el').
  - More-specific-but-consistent answers count 1 (Q010/Q081 'Milli Parkı'/'National Park'; Q158 'Artistik buz pateni'; Q145 1953 ⊂ 1950'ler).
  - Date/scope contradictions count 0 (Q078 1947-1976 vs 1950'ler-70'ler; Q134 different assessment).
  - Truncated-but-started-correct answers count 0 when the distinctive tail is missing (Q152).
  - Rater stayed blind: read only the package CSV; did not consult scorer internals while labeling (frozen policy text only, from the calibration script docstring known beforehand).
