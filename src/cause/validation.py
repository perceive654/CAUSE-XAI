# src/cause/validation.py

import numpy as np


def check_roundtrip(anm, x):
    """
    Check forward(inverse(x)) ≈ x.

    Returns
    -------
    dict
        {"max_error": float, "mean_error": float}
    """
    u = anm.inverse(x)
    x_rec = anm.forward(u)
    err = np.abs(x - x_rec)
    return {
        "max_error": float(np.max(err)),
        "mean_error": float(np.mean(err)),
    }


def sample_violation_stats(anm, x=None, K=200, scale=0.5, seed=0):
    """
    Sample K noise-space counterfactuals u = u0 + N(0, scale*I)
    and compute violation statistics.

    Returns
    -------
    dict
        {"mean": float, "median": float, "std": float,
         "p5": float, "p95": float, "max": float}
    """
    rng = np.random.default_rng(seed)
    p = anm.p
    if x is not None:
        u0 = anm.inverse(x)
    else:
        u0 = rng.normal(size=anm.p)
    viols = []
    for _ in range(K):
        u = u0 + rng.normal(size=p) * scale
        x = anm.forward(u)
        viols.append(anm.violation(x))

    viols = np.array(viols)
    return {
        "mean": float(np.mean(viols)),
        "median": float(np.median(viols)),
        "std": float(np.std(viols)),
        "p5": float(np.percentile(viols, 5)),
        "p95": float(np.percentile(viols, 95)),
        "max": float(np.max(viols)),
    }


def check_dag(adj, order):
    """
    Basic DAG checks.

    Returns
    -------
    dict
        {
          "is_acyclic": bool,
          "topo_violations": list of (parent, child) where
            position[parent] > position[child],
        }
    """
    import networkx as nx

    G = nx.DiGraph(np.argwhere(adj).tolist())
    is_acyclic = nx.is_directed_acyclic_graph(G)

    position = {node: i for i, node in enumerate(order)}
    violations = []
    for parent in range(adj.shape[0]):
        for child in range(adj.shape[1]):
            if adj[parent, child]:
                if position[parent] > position[child]:
                    violations.append((parent, child))

    return {
        "is_acyclic": is_acyclic,
        "topo_violations": violations,
    }