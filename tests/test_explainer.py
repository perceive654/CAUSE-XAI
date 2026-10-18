import numpy as np

from cause import CCE_ANM_Model


def test_explainer_unfitted():
    model = CCE_ANM_Model()
    x_obs = np.array([0.1, 0.2, 0.3])

    try:
        model.explain(x_obs, y_foil=1.0)
    except RuntimeError:
        return

    assert False, "Expected RuntimeError"


def test_explainer_basic():
    rng = np.random.default_rng(2)
    n = 200

    X1 = rng.normal(size=n)
    X2 = 1.5 * X1 + rng.normal(scale=0.5, size=n)
    X3 = 1.2 * X2 + rng.normal(scale=0.5, size=n)
    X = np.column_stack([X1, X2, X3])

    f = lambda Xin: 1.0 / (
        1.0 + np.exp(-(Xin[:, 1] + Xin[:, 2]))
    )

    model = CCE_ANM_Model(
        lambda_=1.0,
        K_cce=20,
        K_cai=60,
        top_k=3,
    )

    model.fit(X, f, verbose=False)

    x_obs = X[0]
    y_foil = 1.0

    result = model.explain(
        x_obs,
        y_foil,
        verbose=False,
    )

    assert result.x_obs.shape == x_obs.shape
    assert result.cce is not None
    assert result.cai is not None
    assert result.cce.x_star.shape == x_obs.shape
    assert result.cai.cai.shape == (3,)