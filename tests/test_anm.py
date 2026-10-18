# tests/test_anm.py

import numpy as np
from scipy.stats import laplace as sp_laplace

from cause.anm import ANM
from cause.validation import check_roundtrip, sample_violation_stats, check_dag


def test_roundtrip_chain(chain_anm):
    adj, order = chain_anm

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

    anm = ANM(adj, order)
    anm.fit(X, verbose=False)

    x0 = X[0]
    stats = check_roundtrip(anm, x0)

    assert stats["max_error"] < 1e-3
    print(
    f"\nRoundtrip error: {stats['max_error']:.2e}  → "
    f"{'✅ PASS' if stats['max_error'] < 1e-3 else '❌ FAIL'}"
)


def test_violation_stats_chain(chain_anm):
    adj, order = chain_anm

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

    anm = ANM(adj, order)
    anm.fit(X, verbose=False)

    stats = sample_violation_stats(anm, K=200, scale=0.5, seed=2)
    print(
        f"Noise-space CFs mean V_M = {stats['mean']:.3f} "
        f"(on-manifold ≈ O(1))"
    )
    # Typical noise-level violations should be O(1), not huge
    assert 0.1 < stats["mean"] < 5.0
    print("✅ ANM validated")


def test_dag_checks(chain_anm):
    adj, order = chain_anm
    info = check_dag(adj, order)
    assert info["is_acyclic"]
    assert len(info["topo_violations"]) == 0