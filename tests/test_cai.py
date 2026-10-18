import numpy as np

from cause import CCE_ANM_Model


def test_attribute_basic():
    rng = np.random.default_rng(1)
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

    cai_result = model.attribute(
        x_obs,
        verbose=False,
    )

    assert cai_result.cai.shape == (3,)
    assert cai_result.baseline is not None
    assert np.all(np.isfinite(cai_result.cai))