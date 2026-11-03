# Referee review package — "The Rule of 40 as a Price Line" (Murthy, Nov 2026)

- referee_report.md — the consolidated panel report (deliverables A–H: editorial
  assessment; audit matrix; findings; empirical assessment; citation ledger;
  verification inventory; revision sequence; uncertainty statement).
- SOURCE_MANIFEST.md — frozen evidence boundary: supplied files, hashes, version
  drift, pagination conventions, quarantine record, panel rules.
- first_reports/ — the five preserved specialist first reports (A math, B econometrics,
  C accounting, D reliability/controls, E prior art) + the Lead's pre-panel argument
  reconstruction. Written in isolation; not edited afterwards.
- adversarial_audit/F_audit.md — referee F's attack on all candidate findings (zero
  withdrawals; two narrowed further; per-finding dispositions, dedupe, severity triage,
  circularity attacks, locator spot-checks).
- diagnostics/ — all independent verification scripts with raw outputs and seeds
  (Lead checks; A's symbolic/numeric/HJB checks; A2's U-shape investigation; B's
  independent reimplementation + reduced bootstrap + Holm counterfactuals; C's case
  recomputations and fetched filings texts; D's Monte Carlo and primary-source ledger;
  E's fetched primary sources and ledger data).
- execution_logs/full_bootstrap_replication.md — the full 999-replication pipeline
  rerun and its diff against the author's committed outputs.

Environment: Python 3.12.3; numpy 2.5.2, scipy 1.18.1, sympy 1.14.0, pandas 3.0.3,
statsmodels 0.15.0. Fixed seeds (base 20261103). All panel members are LLM agents
(single model family, one harness); see report §0 for the model-identity disclosure.
