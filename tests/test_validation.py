# tests/test_validation.py

import numpy as np
from scipy.stats import laplace as sp_laplace

from cause.anm import ANM
from cause.validation import check_roundtrip, sample_violation_stats, check_dag


def test_check_roundtrip():
    rng = np.random.default_rng(0)
    n = 300
    U1 = sp_laplace.rvs(scale=1.0, size=n, random_state=rng.integers(2**30))
    U2 = sp_laplace.rvs(scale=0.5, size=n, random_state=rng.integers(2**30))
    U3 = sp_laplace.rvs(scale=0.5, size=n, random_state=rng.integers(2**30))

    X = np.column_stack(
        [
            U1,
            np.tanh(U1) + U2,
            0.5 * (np.tanh(U1) + U2) ** 2 + U3,
        ]
    )

    adj = np.array([[0, 1, 0], [0, 0, 1], [0, 0, 0]])
    order = [0, 1, 2]

    anm = ANM(adj, order)
    anm.fit(X, verbose=False)

    stats = check_roundtrip(anm, X[0])
    assert stats["max_error"] < 1e-3


def test_sample_violation_stats():
    rng = np.random.default_rng(1)
    n = 300
    U1 = sp_laplace.rvs(scale=1.0, size=n, random_state=rng.integers(2**30))
    U2 = sp_laplace.rvs(scale=0.5, size=n, random_state=rng.integers(2**30))
    U3 = sp_laplace.rvs(scale=0.5, size=n, random_state=rng.integers(2**30))

    X = np.column_stack(
        [
            U1,
            np.tanh(U1) + U2,
            0.5 * (np.tanh(U1) + U2) ** 2 + U3,
        ]
    )

    adj = np.array([[0, 1, 0], [0, 0, 1], [0, 0, 0]])
    order = [0, 1, 2]

    anm = ANM(adj, order)
    anm.fit(X, verbose=False)

    stats = sample_violation_stats(anm, K=100, scale=0.5, seed=2)
    assert 0.1 < stats["mean"] < 5.0


def test_check_dag():
    adj = np.array([[0, 1, 0], [0, 0, 1], [0, 0, 0]])
    order = [0, 1, 2]

    info = check_dag(adj, order)
    assert info["is_acyclic"]
    assert len(info["topo_violations"]) == 0