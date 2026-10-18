# tests/test_dag.py

import numpy as np
from cause.dag import discover_dag, hsic, _residuals


def test_hsic_independence():
    rng = np.random.default_rng(0)
    n = 300
    X = rng.normal(size=n)
    Y = rng.normal(size=n)

    # X and Y independent → HSIC should be small (not exactly zero)
    h = hsic(X, Y)
    assert 0.0 <= h < 0.02


def test_residuals_shape():
    rng = np.random.default_rng(1)
    n = 100
    cause = rng.normal(size=n)
    effect = 2.0 * cause + rng.normal(scale=0.5, size=n)

    res = _residuals(cause, effect, n_splits=5)
    assert res.shape == (n,)


def test_discover_dag_chain():
    rng = np.random.default_rng(2)
    n = 400
    U1 = rng.normal(size=n)
    U2 = rng.normal(scale=0.5, size=n)
    U3 = rng.normal(scale=0.5, size=n)

    X1 = U1
    X2 = 1.5 * X1 + U2
    X3 = 1.2 * X2 + U3

    X = np.column_stack([X1, X2, X3])

    adj, order = discover_dag(X, verbose=False)

    # At minimum, graph should be a DAG
    import networkx as nx
    G = nx.DiGraph(np.argwhere(adj).tolist())
    assert nx.is_directed_acyclic_graph(G)