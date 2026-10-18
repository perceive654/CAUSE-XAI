# examples/basic_synthetic_demo.py

import numpy as np
from scipy.stats import laplace as sp_laplace

from cause import ANM, discover_dag, CCE_ANM_Model


def make_chain_anm(n=500, seed=0):
    rng = np.random.default_rng(seed)
    U1 = sp_laplace.rvs(scale=1.0, size=n, random_state=rng.integers(2**30))
    U2 = sp_laplace.rvs(scale=0.5, size=n, random_state=rng.integers(2**30))
    U3 = sp_laplace.rvs(scale=0.5, size=n, random_state=rng.integers(2**30))

    X1 = U1
    X2 = np.tanh(X1) + U2
    X3 = 0.5 * (np.tanh(X1) + U2) ** 2 + U3

    X = np.column_stack([X1, X2, X3])
    return X


def main():
    X = make_chain_anm(n=500)

    # Learn DAG and ANM
    adj, order = discover_dag(X, verbose=True)
    print("\nLearned adjacency:\n", adj)
    print("Order:", order)

    anm = ANM(adj, order)
    anm.fit(X, verbose=True)

    # Simple black-box predictor for demo
    f = lambda Xin: 1.0 / (1.0 + np.exp(-(Xin[:, 1] + Xin[:, 2])))

    model = CCE_ANM_Model(
        lambda_=1.0, K_cce=20, K_cai=80, n_restarts=3, top_k=3
    )
    model.fit(X, f, verbose=True)

    x_obs = X[0]
    y_foil = 1.0
    result = model.explain(x_obs, y_foil, verbose=True)
    result.summary()


if __name__ == "__main__":
    main()