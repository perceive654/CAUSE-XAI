# CAUSE Architecture

CAUSE is a modular Python package derived from the verified CCE-ANM implementation. The package separates the public model interface, causal computation, diagnostics, structured results, and notebook-oriented display.

## Current package structure

```text
src/
└── cause/
    ├── __init__.py
    ├── model.py
    ├── anm.py
    ├── dag.py
    ├── cce.py
    ├── cai.py
    ├── diagnostics.py
    ├── results.py
    └── display.py
```

## Module responsibilities

### `model.py`

Public `CCE_ANM_Model` orchestration layer. Main methods:

```text
fit()
counterfactual()
attribute()
explain()
comp_shap_cai()
```

It owns the fitted causal state and connects computation with user-facing display.

### `anm.py`

Additive Noise Model implementation:

- structural equations;
- Gaussian Process fitting;
- forward/inverse transformations;
- ANM sampling and intervention sampling;
- node-specific residual noise;
- violation and consistency operations.

### `dag.py`

Exploratory graph-learning utilities:

- HSIC;
- pairwise ANM residual tests;
- DAG discovery;
- percentile thresholding;
- cycle removal;
- topological ordering.

### `cce.py`

Causal Counterfactual Explanation search:

- observed noise-space representation;
- CAI-guided candidate ranking;
- sparse intervention search;
- positive/negative ray search;
- non-actionable direct-intervention filtering;
- target/feasibility checks;
- `CCEResult` construction.

### `cai.py`

Causal Attribution via Interventions:

- baseline Monte Carlo sampling;
- feature-wise interventions;
- common random numbers;
- paired causal effects;
- standard errors and confidence intervals;
- variance-reduction diagnostics;
- `CAIResult` construction.

### `diagnostics.py`

CAI-versus-SHAP-style comparison and related disagreement diagnostics.

### `results.py`

Structured public result objects:

```text
CCEResult
CAIResult
UnifiedExplanation
```

The result layer also provides `to_dict()` for JSON-ready application output. It does not perform the causal calculations.

### `display.py`

Presentation-only functions:

```text
show_fit()
show_counterfactual()
show_attribution()
show_explanation()
show_cai_vs_shap()
show_dag()
```

These format already-computed results. Core causal modules do not depend on display functions.

## High-level data flow

```text
                    User data X + prediction function
                               │
                               ▼
                    ┌────────────────────┐
                    │   CCE_ANM_Model    │
                    │       fit()        │
                    └─────────┬──────────┘
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
          supplied DAG              exploratory DAG
                 │                         │
                 └────────────┬────────────┘
                              ▼
                         fitted ANM
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
             CAI             CCE         diagnostics
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                       result objects
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                to_dict()           display()
                    │                   │
                    ▼                   ▼
                 JSON/API          human-readable
```

## Public API boundary

The intended import is:

```python
from cause import CCE_ANM_Model
```

Typical use:

```python
model = CCE_ANM_Model(
    adjacency_matrix=adjacency_matrix,
    feature_names=feature_names,
    random_state=42,
)

model.fit(X, predict_fn)
cce = model.counterfactual(x_observed, y_foil=1)
cai = model.attribute(x_observed)
explanation = model.explain(x_observed, y_foil=1)
comparison = model.comp_shap_cai(x_observed)
```

The public result types are also intended for developer use. Internal helper functions, latent noise values, search state, and temporary numerical structures are not stable API commitments.

## Prediction-function boundary

The black-box predictor is supplied to the model and must satisfy the binary-classification scoring contract:

```python
predict_fn(X: np.ndarray) -> np.ndarray
```

with:

```text
X      : (n_samples, n_features)
scores : (n_samples,)
```

Scores must be finite positive-class probabilities/scores within the supported `[0, 1]` range.

## Preprocessing boundary

Users provide raw continuous numerical features. CAUSE performs the internal causal-model preprocessing required by the ANM. User-facing counterfactual values are returned in the original feature units.

## CCE and CAI relationship

Both explanation types operate on the same fitted ANM:

```text
                         fitted ANM
                            │
                  ┌─────────┴─────────┐
                  │                   │
                 CAI                 CCE
                  │                   │
          causal feature       sparse intervention
             ranking                search
                  │                   │
                  └─────────┬─────────┘
                            ▼
                    unified explanation
```

CAI estimates feature-level interventional effects. CCE uses CAI to prioritize intervention candidates and then performs the sparse counterfactual search.

## Non-actionable features

A CCE `non_actionable` feature is excluded from **direct intervention candidates**. It is not necessarily fixed in the resulting causal state.

For a graph:

```text
A → B → C
```

an intervention on `A` can cause `B` and `C` to change. Therefore:

```text
direct interventions ≠ all changed features
```

CAI evaluates feature effects independently and is not automatically restricted by the CCE non-actionable list.

## Validation philosophy

The package validates public inputs and provides fitted-model diagnostics for:

- input shape and feature count;
- finite numerical values;
- DAG validity;
- prediction-function output shape and range;
- fitted-state requirements;
- ANM round-trip consistency;
- fitted-model violation.

These checks do not establish that the learned causal model is true in the real world.

## Display and computation separation

```text
public model method
        │
        ├── computation
        │
        ├── result object
        │
        └── verbose=True → display function
```

This allows one result to be displayed in Jupyter, converted to a dictionary, serialized as JSON, or consumed programmatically without parsing printed output.

## Design principles

The current package retains the core library-conversion principles:

1. Modular separation of causal components.
2. Small public API around `CCE_ANM_Model`.
3. Local deterministic random generators.
4. Explicit input and prediction validation.
5. Structured result objects.
6. JSON-ready output.
7. Computation/display separation.
8. No network, telemetry, or automatic cloud persistence.
9. Original feature units at the user-facing boundary.
10. Notebook code remains a research/reference artifact rather than the importable package.

## What is not promised

CAUSE does not guarantee that:

- an automatically discovered DAG is the true causal graph;
- ANM assumptions are correct for a real-world system;
- latent confounding has been eliminated;
- a generated counterfactual is actionable;
- a CAI value is a real-world causal effect outside the fitted model;
- internal implementation helpers remain stable across versions.

The compatibility boundary is the documented public API and result objects.
