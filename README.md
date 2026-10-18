# CAUSE-XAI

**Causal Additive-noise Unified Explanation**

CAUSE-XAI is a local Python library for explaining a black-box **binary
classifier** using a learned causal DAG and a fitted **Additive Noise
Model (ANM)**.

The library provides:

-   **CCE --- Causal Counterfactual Explanation:** searches for a sparse
    causal counterfactual that moves a prediction toward a requested
    target while respecting the learned causal structure.
-   **CAI --- Causal Attribution via Interventions:** estimates
    feature-level causal effects through interventions in the fitted
    ANM.
-   **CAI-vs-SHAP-style comparison:** provides a diagnostic comparison
    between interventional causal attribution and an observational
    SHAP-style attribution.

CAUSE-XAI does **not** establish that a learned DAG represents
real-world causality. Explanations are conditional on the learned graph,
ANM assumptions, fitted structural equations, noise model, and the
absence of important unmodeled confounding.

## Features

-   Local execution; no network calls, telemetry, accounts, or cloud
    storage.
-   Continuous numerical tabular data.
-   Binary-classification explanations.
-   Automatic exploratory DAG discovery.
-   Gaussian-process structural equations with Laplace residual-noise
    models.
-   Causal counterfactual search in ANM noise space.
-   CAI-guided CCE candidate ranking.
-   Monte Carlo interventional causal attribution with common random
    numbers.
-   Support for non-actionable features in direct CCE intervention
    search.
-   ANM round-trip and violation diagnostics.
-   Structured result objects with `to_dict()` and `to_json()`.
-   Separate computation and presentation layers.
-   Deterministic local random generators through `random_state`.

## Installation

### Development installation

``` bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run the test suite:

``` bash
python3 -m pytest -q
```

### Package installation

``` bash
pip install cause-xai
```

Import the package as:

``` python
from cause import CCE_ANM_Model
```

## Quick Start

The public API accepts raw continuous numerical background data.
CAUSE-XAI standardizes the data internally before DAG discovery and ANM
fitting. Therefore, the supplied black-box prediction function must
operate on the same standardized representation.

``` python
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier

from cause import CCE_ANM_Model

# 1. Background data
rng = np.random.default_rng(0)
n = 500

x1 = rng.normal(size=n)
x2 = np.tanh(x1) + 0.5 * rng.normal(size=n)
x3 = 0.5 * (x1 + x2) + 0.3 * rng.normal(size=n)

X = np.column_stack([x1, x2, x3])
y = (x3 + 0.2 * rng.normal(size=n) > np.median(x3)).astype(int)

# 2. Train the black-box model on the standardized representation
predictor_scaler = StandardScaler().fit(X)
X_model = predictor_scaler.transform(X)

clf = GradientBoostingClassifier(random_state=0).fit(X_model, y)

def predict_fn(X_input):
    return clf.predict_proba(X_input)[:, 1]

# 3. Fit CAUSE-XAI
model = CCE_ANM_Model(random_state=42)
model.fit(X, predict_fn, verbose=True)

# 4. Explain one observation
x_observed = X[0]

cce = model.counterfactual(x_observed, y_foil=1, verbose=True)
cai = model.attribute(x_observed, verbose=True)
explanation = model.explain(x_observed, y_foil=1, verbose=True)
comparison = model.comp_shap_cai(x_observed, verbose=True)
```

## Public API

The main public interface is `CCE_ANM_Model`.

### Constructor

The verified defaults are:

``` python
model = CCE_ANM_Model(
    lambda_=2.0,
    mu=50.0,
    K_cce=30,
    K_cai=1000,
    top_k=10,
    target_prob=0.55,
    search_feasibility="instance",
    random_state=42,
    percentile=75.0,
    cycle_strategy="weakest",
)
```

### `fit()`

``` python
model.fit(data, f, verbose=True)
```

`data` may be a NumPy array or pandas DataFrame with shape
`(n_samples, n_features)`.

The fitting pipeline is:

1.  accept raw background data;
2.  standardize the data internally;
3.  discover the causal DAG from the standardized data;
4.  fit the ANM on the standardized data;
5.  store the scaler, DAG, ANM, feature metadata, and prediction
    function.

If a DataFrame is supplied, its column names are retained as feature
names. For NumPy arrays, generated feature names are used when needed.

### `counterfactual()`

``` python
result = model.counterfactual(
    x_observed,
    y_foil=1.0,
    non_actionable=["gender"],
    verbose=True,
)
```

`non_actionable` may contain feature names or feature indices. These
features are excluded from **direct CCE intervention candidates**. They
remain part of the causal graph and may still change as downstream
consequences of interventions on their causes.

Returns a `CCEResult`.

### `attribute()`

``` python
result = model.attribute(
    x_observed,
    feature_names=None,
    verbose=True,
)
```

CAI estimates the causal effect of each feature by comparing the
expected black-box output under a feature intervention with the ANM
baseline. Common random numbers are used between baseline and
intervention sampling.

Returns a `CAIResult`.

### `explain()`

``` python
result = model.explain(
    x_observed,
    y_foil=1.0,
    feature_names=None,
    non_actionable=["gender"],
    verbose=True,
)
```

Runs CCE and CAI once and combines them into a `UnifiedExplanation`.

### `comp_shap_cai()`

``` python
comparison = model.comp_shap_cai(
    x_observed,
    K=200,
    verbose=True,
)
```

Runs the diagnostic comparison between interventional CAI and the
observational SHAP-style attribution.

### `explain_all()`

``` python
result = model.explain_all(
    x_observed,
    y_foil=1.0,
    feature_names=None,
    non_actionable=["gender"],
    K=None,
    verbose=True,
)
```

Runs the complete workflow once:

1.  CCE
2.  CAI
3.  CAI-vs-SHAP-style comparison

The returned `UnifiedExplanation` contains the CCE result, CAI result,
and comparison result.

## Prediction Function Contract

The black-box scoring function must accept a two-dimensional array and
return one positive-class score per row:

``` python
def predict_fn(X_input: np.ndarray) -> np.ndarray:
    ...
```

Expected shapes:

``` text
X_input : (n_samples, n_features)
output  : (n_samples,)
```

The output must contain finite binary-classification
scores/probabilities in the supported `[0, 1]` range.

For scikit-learn classifiers:

``` python
def predict_fn(X_input):
    return clf.predict_proba(X_input)[:, 1]
```

## Input Boundary

### Background data

`fit()` accepts NumPy arrays and pandas DataFrames.

``` text
(n_samples, n_features)
```

The features must be continuous numerical variables.

### Individual observations

Explanation methods accept one observation as either:

``` text
(n_features,)
```

or:

``` text
(1, n_features)
```

Public observations are supplied in raw feature units. CAUSE-XAI
transforms them internally using the scaler fitted during `fit()`.

## Causal DAG

The DAG is discovered automatically from the standardized background
data.

The adjacency convention is:

``` text
adjacency_matrix[i, j] == 1
    means feature i is a parent of feature j
```

DAG discovery uses pairwise HSIC/ANM-based orientation, percentile-based
edge selection, cycle handling, and topological ordering.

Automatic DAG discovery is exploratory. Where domain knowledge is
available, the learned graph should be reviewed before interpreting
results causally.

## CCE Interpretation

CCE searches in the fitted ANM's latent noise space. Candidate
interventions are guided by CAI feature ranking and evaluated through
progressive sparse search and one-dimensional positive/negative ray
searches.

The result distinguishes between:

-   **direct interventions** --- variables directly modified by the CCE
    search;
-   **downstream changes** --- variables that change because the
    intervention propagates through the learned causal graph.

Therefore:

``` text
direct interventions != all changed features
```

A CCE is a model-based counterfactual. It is not a guarantee that the
implied real-world change is actionable, affordable, legal, or
physically feasible.

### Non-actionable features

Use `non_actionable` for variables that must not be selected as direct
intervention targets, for example an immutable attribute:

``` python
cce = model.counterfactual(
    x_observed,
    y_foil=1,
    non_actionable=["gender"],
)
```

The feature remains in the causal model and may change indirectly if its
causal parents are intervened on.

## CAI Interpretation

For feature `j`, CAI estimates:

``` text
CAI_j = E[f(X) | do(X_j = x_observed[j])] - E[f(X)]
```

using Monte Carlo sampling from the fitted ANM.

The implementation uses common random numbers between baseline and
intervention sampling, providing paired causal-effect estimates with
standard errors and confidence intervals.

`non_actionable` does not restrict CAI. CAI estimates the causal effect
of every feature.

## Results

The main structured result objects are:

``` text
CCEResult
CAIResult
UnifiedExplanation
```

Results are intended for programmatic use and support JSON-ready
serialization:

``` python
payload = explanation.to_dict()
json_text = explanation.to_json()
```

Serialized results contain user-facing information such as predictions,
counterfactual values, causal attributions, confidence intervals,
changed features, search diagnostics, and feature names. Internal latent
noise and temporary search state are not part of the public
serialization.

## Architecture

CAUSE-XAI separates public orchestration, causal computation,
diagnostics, structured results, and presentation.

``` text
src/cause/
├── __init__.py
├── explainer.py
├── config.py
├── exceptions.py
├── validation.py
├── anm.py
├── dag.py
├── cce.py
├── cai.py
├── diagnostics.py
├── results.py
└── display.py
```

### `explainer.py`

Public `CCE_ANM_Model` orchestration layer. It owns the fitted scaler,
prediction function, DAG, ANM, feature metadata, and public workflows.

### `dag.py`

Exploratory DAG discovery and graph-learning operations, including
HSIC/ANM-based pairwise orientation, thresholding, cycle handling, and
topological ordering.

### `anm.py`

Additive Noise Model implementation, including structural equations,
Gaussian-process regression, forward/inverse transformations, Laplace
residual noise, sampling, interventions, and consistency/violation
operations.

### `cce.py`

Causal counterfactual search, including:

-   observed noise-space representation;
-   CAI-guided candidate ranking;
-   progressive sparse intervention search;
-   positive/negative ray search;
-   non-actionable direct-intervention filtering;
-   target and feasibility checks;
-   `CCEResult` construction.

### `cai.py`

Causal Attribution via Interventions, including:

-   baseline Monte Carlo sampling;
-   feature-wise interventions;
-   common random numbers;
-   paired causal effects;
-   standard errors and confidence intervals;
-   variance-reduction diagnostics;
-   `CAIResult` construction.

### `diagnostics.py`

CAI-vs-SHAP-style comparison and related fitted-model diagnostics.

### `results.py`

Structured public result objects. This layer serializes already-computed
results and does not perform causal calculations.

### `display.py`

Presentation-only functions for human-readable notebook output. Core
numerical modules do not depend on display functions.

### `validation.py` and `exceptions.py`

Input/model-state validation and package-specific exception types.

## Data Flow

``` text
                    Raw X + prediction function
                               │
                               ▼
                    ┌────────────────────┐
                    │   CCE_ANM_Model    │
                    │      fit()         │
                    └─────────┬──────────┘
                              │
                    StandardScaler transform
                              │
                              ▼
                    ┌────────────────────┐
                    │   DAG discovery    │
                    └─────────┬──────────┘
                              │
                              ▼
                       fitted ANM model
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
            CAI              CCE          diagnostics
             │                │                │
             └────────────────┼────────────────┘
                              ▼
                        result objects
                              │
                       ┌──────┴──────┐
                       ▼             ▼
                    to_dict()     display
                       │             │
                       ▼             ▼
                   JSON/API    human-readable
```

The public model methods perform computation first and call the display
layer only when requested. Internal numerical modules do not perform
user-facing rendering.

## Diagnostics

CAUSE-XAI includes diagnostics for:

-   ANM forward/inverse round-trip consistency;
-   ANM violation behavior;
-   CAI-vs-SHAP-style comparison;
-   Monte Carlo variance-reduction information.

These diagnostics assess the fitted model and computational behavior.
They do not prove real-world causal validity.

## Limitations

-   Continuous numerical tabular features are supported; categorical and
    mixed-type data are not currently supported.
-   The current implementation is for binary-classification outputs.
-   CCE and CAI are conditional on the fitted/discovered DAG and ANM
    assumptions.
-   CAUSE-XAI does not prove real-world causality.
-   Unobserved confounding can invalidate causal interpretation.
-   Gaussian-process structural equations can become expensive for large
    datasets.
-   Residual noise is modeled using the implemented Laplace-noise
    formulation.
-   CAI is Monte Carlo estimated and therefore has sampling uncertainty.
-   Automatic DAG discovery is exploratory and should not replace
    domain-validated causal knowledge.
-   A generated counterfactual is not automatically guaranteed to be
    practically actionable.

## Development and Testing

``` bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python3 -m pytest -q
```

Before a release, build the package and verify the resulting artifacts
in a clean environment:

``` bash
python3 -m build
```

## Version

Current package version: `0.1.0`

<!-- ## License

MIT. -->
