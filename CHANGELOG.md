# Changelog

All notable changes to this project are documented in this file.

## [0.1.0] - Initial release

### Added
- `ANM`: additive noise model with Gaussian Process structural equations and
  Laplace-distributed noise, supporting `fit`, `forward`, `inverse`,
  `do_sample`, `sample`, and `violation` diagnostics.
- `validate_anm`: numerical consistency validation (roundtrip error and
  sample-violation checks) for a fitted `ANM`.
- `compute_cai`: Causal Attribution via Interventions (CAI), an interventional
  attribution method based on do-style sampling from the fitted ANM.
- `generate_counterfactual`: Causal Counterfactual Explanations (CCE), a
  noise-space search for a minimal, causally consistent counterfactual that
  flips a black-box binary classifier's prediction.
- `discover_dag` and `hsic`: optional, explicitly exploratory pairwise-HSIC
  based DAG discovery.
- `CAUSEExplainer`: unified public API wiring ANM fitting, validation, CCE,
  and CAI together.
- Typed result containers: `CCEResult`, `CAIResult`, `ValidationResult`,
  `UnifiedExplanation`.
- Example scripts for a synthetic ANM demo and a breast-cancer demo (using an
  illustrative, non-medical DAG).
- Full pytest test suite covering ANM, validation, CAI, CCE, DAG discovery,
  and the end-to-end explainer flow.

### Scope and limitations
- V0.1.0 supports numerical continuous features and binary classification
  only. See the README "Limitations" section for the full list of
  assumptions and constraints.
