# # import numpy as np
# # from itertools import combinations

# # from sklearn.gaussian_process import GaussianProcessRegressor
# # from sklearn.gaussian_process.kernels import RBF, WhiteKernel
# # from sklearn.model_selection import KFold


# # # ============================================================
# # # BANDWIDTH
# # # ============================================================

# # def _bw(X):
# #     """
# #     Median heuristic bandwidth for the RBF kernel.

# #     This follows the notebook implementation.
# #     """
# #     X = np.asarray(X)

# #     if X.ndim == 1:
# #         X = X.reshape(-1, 1)

# #     n = len(X)

# #     idx = np.random.choice(
# #         n,
# #         min(n, 300),
# #         replace=False,
# #     )

# #     d = np.sqrt(
# #         (
# #             X[idx, None]
# #             - X[None, idx, :]
# #         ) ** 2
# #     ).sum(-1)

# #     m = np.median(
# #         d[d > 0]
# #     )

# #     return float(m) if m > 0 else 1.0


# # # ============================================================
# # # RBF KERNEL
# # # ============================================================

# # def _K(X, bw):
# #     """
# #     RBF kernel matrix.

# #     This follows the notebook implementation.
# #     """
# #     X = np.asarray(X)

# #     if X.ndim == 1:
# #         X = X.reshape(-1, 1)

# #     return np.exp(
# #         -(
# #             (X[:, None] - X[None, :]) ** 2
# #         ).sum(-1)
# #         / (2 * bw ** 2)
# #     )


# # # ============================================================
# # # HSIC
# # # ============================================================

# # def hsic(X, Y, bw=None):
# #     """
# #     Compute the biased HSIC estimator.

# #         HSIC = (1 / n^2) tr(K_c L_c)

# #     The notebook uses:
# #     - median heuristic bandwidth
# #     - RBF kernels
# #     - centered kernel matrices
# #     - biased HSIC estimator
# #     """
# #     bx = bw or _bw(X)
# #     by = bw or _bw(Y)

# #     n = len(X)

# #     H = (
# #         np.eye(n)
# #         - 1.0 / n
# #     )

# #     Kc = (
# #         H
# #         @ _K(X, bx)
# #         @ H
# #     )

# #     Lc = (
# #         H
# #         @ _K(Y, by)
# #         @ H
# #     )

# #     return float(
# #         np.trace(Kc @ Lc)
# #         / (n ** 2)
# #     )


# # # ============================================================
# # # ANM RESIDUALS
# # # ============================================================

# # def _residuals(
# #     cause,
# #     effect,
# #     n_splits=5,
# #     random_state=42,
# # ):
# #     """
# #     Estimate ANM residuals using K-fold cross-fitting.

# #     For:

# #         cause -> effect

# #     fit:

# #         effect = g(cause) + U

# #     and return:

# #         U = effect - g_hat(cause)

# #     This is the same residual-generation logic used
# #     by the notebook's DAG discovery.
# #     """
# #     cause = np.asarray(cause)
# #     effect = np.asarray(effect)

# #     n = len(cause)

# #     if n != len(effect):
# #         raise ValueError(
# #             "cause and effect must have "
# #             "the same length"
# #         )

# #     if n < n_splits:
# #         raise ValueError(
# #             f"Number of samples ({n}) must be "
# #             f">= n_splits ({n_splits})"
# #         )

# #     residuals = np.empty(n)

# #     kf = KFold(
# #         n_splits=n_splits,
# #         shuffle=True,
# #         random_state=random_state,
# #     )

# #     for train_idx, test_idx in kf.split(cause):

# #         gp = GaussianProcessRegressor(
# #             kernel=RBF() + WhiteKernel(),
# #             alpha=1e-3,
# #             normalize_y=True,
# #             n_restarts_optimizer=0,
# #         )

# #         gp.fit(
# #             cause[train_idx].reshape(-1, 1),
# #             effect[train_idx],
# #         )

# #         predictions = gp.predict(
# #             cause[test_idx].reshape(-1, 1)
# #         )

# #         residuals[test_idx] = (
# #             effect[test_idx]
# #             - predictions
# #         )

# #     return residuals


# # # ============================================================
# # # DAG DISCOVERY
# # # ============================================================

# # def discover_dag(
# #     data,
# #     verbose=True,
# # ):
# #     """
# #     Discover a sparse DAG using pairwise ANM + HSIC.

# #     Notebook logic:

# #     For every pair (i, j):

# #         1. Fit Xi -> Xj
# #         2. Fit Xj -> Xi
# #         3. Compute HSIC(residual, proposed cause)
# #         4. Lower HSIC determines the candidate direction
# #         5. Absolute HSIC difference is used as confidence
# #         6. Keep candidates whose confidence is at or above
# #            the 75th percentile
# #         7. Remove cycles
# #         8. Return adjacency matrix and topological order

# #     This is exploratory pairwise DAG discovery. It does not
# #     condition on other variables and therefore can produce
# #     indirect or spurious edges.
# #     """
# #     import networkx as nx

# #     data = np.asarray(
# #         data,
# #         dtype=float,
# #     )

# #     if data.ndim != 2:
# #         raise ValueError(
# #             "data must be a 2D array "
# #             "(n_samples, n_features)"
# #         )

# #     n, p = data.shape

# #     adj = np.zeros(
# #         (p, p),
# #         dtype=int,
# #     )

# #     hsic_diffs = []
# #     edge_candidates = []

# #     if verbose:
# #         print(
# #             f"  DAG discovery: "
# #             f"{p} vars, "
# #             f"{p * (p - 1) // 2} pairs..."
# #         )

# #     # --------------------------------------------------------
# #     # Pairwise ANM orientation
# #     # --------------------------------------------------------

# #     for i, j in combinations(
# #         range(p),
# #         2,
# #     ):

# #         # Same notebook sampling logic
# #         idx = np.random.choice(
# #             n,
# #             min(n, 500),
# #             replace=False,
# #         )

# #         # ----------------------------------------------------
# #         # Forward: Xi -> Xj
# #         # ----------------------------------------------------

# #         Rf = _residuals(
# #             data[idx, i],
# #             data[idx, j],
# #         )

# #         # ----------------------------------------------------
# #         # Reverse: Xj -> Xi
# #         # ----------------------------------------------------

# #         Rr = _residuals(
# #             data[idx, j],
# #             data[idx, i],
# #         )

# #         # ----------------------------------------------------
# #         # HSIC
# #         # ----------------------------------------------------

# #         hf = hsic(
# #             Rf,
# #             data[idx, i],
# #         )

# #         hr = hsic(
# #             Rr,
# #             data[idx, j],
# #         )

# #         # ----------------------------------------------------
# #         # Confidence
# #         # ----------------------------------------------------

# #         diff = abs(
# #             hf - hr
# #         )

# #         hsic_diffs.append(
# #             diff
# #         )

# #         # ----------------------------------------------------
# #         # Candidate orientation
# #         # ----------------------------------------------------

# #         if hf < hr:

# #             edge_candidates.append(
# #                 (i, j, diff)
# #             )

# #             direction = (
# #                 f"X{i + 1}→X{j + 1}"
# #             )

# #         else:

# #             edge_candidates.append(
# #                 (j, i, diff)
# #             )

# #             direction = (
# #                 f"X{j + 1}→X{i + 1}"
# #             )

# #         if verbose:
# #             print(
# #                 f"    {direction}  "
# #                 f"HSIC("
# #                 f"fwd={hf:.5f}, "
# #                 f"rev={hr:.5f}"
# #                 f")"
# #             )

# #     # --------------------------------------------------------
# #     # Dynamic confidence threshold
# #     # --------------------------------------------------------

# #     if len(hsic_diffs) == 0:

# #         threshold = 0.0

# #     else:

# #         threshold = np.percentile(
# #             hsic_diffs,
# #             75,
# #         )

# #     if verbose:
# #         print(
# #             f"\nEdges before thresholding: "
# #             f"{len(edge_candidates)}"
# #         )

# #         print(
# #             "Dynamic HSIC threshold "
# #             f"(75th percentile): "
# #             f"{threshold:.6f}"
# #         )

# #     # --------------------------------------------------------
# #     # Keep high-confidence edges
# #     # --------------------------------------------------------

# #     for u, v, d in edge_candidates:

# #         if d >= threshold:
# #             adj[u, v] = 1

# #     if verbose:
# #         print(
# #             f"Edges after thresholding: "
# #             f"{adj.sum()}"
# #         )

# #     # --------------------------------------------------------
# #     # Remove cycles
# #     # --------------------------------------------------------

# #     while True:

# #         G = nx.DiGraph(
# #             np.argwhere(adj).tolist()
# #         )

# #         try:

# #             cycle = nx.find_cycle(G)

# #             u, v = cycle[0]

# #             adj[u, v] = 0

# #         except nx.NetworkXNoCycle:

# #             break

# #     # --------------------------------------------------------
# #     # DAG validation
# #     # --------------------------------------------------------

# #     G = nx.DiGraph(
# #         np.argwhere(adj).tolist()
# #     )

# #     if verbose:

# #         print(
# #             f"DAG valid: "
# #             f"{nx.is_directed_acyclic_graph(G)}"
# #         )

# #         print(
# #             f"Edges after cycle removal: "
# #             f"{adj.sum()}"
# #         )

# #     # --------------------------------------------------------
# #     # Topological ordering
# #     # --------------------------------------------------------

# #     in_d = adj.sum(
# #         axis=0
# #     )

# #     q = [
# #         i
# #         for i in range(p)
# #         if in_d[i] == 0
# #     ]

# #     order = []

# #     while q:

# #         v = q.pop(0)

# #         order.append(v)

# #         for j in range(p):

# #             if adj[v, j]:

# #                 in_d[j] -= 1

# #                 if in_d[j] == 0:
# #                     q.append(j)

# #     # Safety fallback for any nodes not included
# #     for i in range(p):

# #         if i not in order:
# #             order.append(i)

# #     return adj, order

# import numpy as np

# from itertools import combinations

# from sklearn.gaussian_process import GaussianProcessRegressor
# from sklearn.gaussian_process.kernels import RBF, WhiteKernel
# from sklearn.model_selection import KFold


# # ============================================================
# # BANDWIDTH
# # ============================================================

# def _bw(
#     X,
#     rng=None,
# ):
#     """
#     Median heuristic bandwidth for the RBF kernel.

#     The bandwidth is estimated from a deterministic local sample
#     when rng is supplied.
#     """
#     X = np.asarray(
#         X,
#         dtype=float,
#     )

#     if X.ndim == 1:
#         X = X.reshape(-1, 1)

#     n = len(X)

#     if n == 0:
#         return 1.0

#     if rng is None:
#         rng = np.random.default_rng(42)

#     idx = rng.choice(
#         n,
#         min(n, 300),
#         replace=False,
#     )

#     d = np.sqrt(
#         (
#             X[idx, None]
#             - X[None, idx, :]
#         ) ** 2
#     ).sum(-1)

#     positive = d[d > 0]

#     if positive.size == 0:
#         return 1.0

#     m = np.median(positive)

#     return (
#         float(m)
#         if np.isfinite(m) and m > 0
#         else 1.0
#     )


# # ============================================================
# # RBF KERNEL
# # ============================================================

# def _K(
#     X,
#     bw,
# ):
#     """
#     RBF kernel matrix.
#     """
#     X = np.asarray(
#         X,
#         dtype=float,
#     )

#     if X.ndim == 1:
#         X = X.reshape(-1, 1)

#     bw = float(bw)

#     if not np.isfinite(bw) or bw <= 0:
#         bw = 1.0

#     return np.exp(
#         -(
#             (
#                 X[:, None]
#                 - X[None, :]
#             ) ** 2
#         ).sum(-1)
#         / (2.0 * bw ** 2)
#     )


# # ============================================================
# # HSIC
# # ============================================================

# def hsic(
#     X,
#     Y,
#     bw=None,
#     rng=None,
# ):
#     """
#     Compute the biased HSIC estimator.

#         HSIC = (1 / n^2) tr(K_c L_c)

#     Notebook logic:

#     - median heuristic bandwidth
#     - RBF kernels
#     - centered kernel matrices
#     - biased HSIC estimator
#     """
#     X = np.asarray(
#         X,
#         dtype=float,
#     )

#     Y = np.asarray(
#         Y,
#         dtype=float,
#     )

#     if X.ndim == 1:
#         X = X.reshape(-1, 1)

#     if Y.ndim == 1:
#         Y = Y.reshape(-1, 1)

#     if len(X) != len(Y):
#         raise ValueError(
#             "X and Y must contain the same number "
#             "of samples."
#         )

#     n = len(X)

#     if n < 2:
#         return 0.0

#     if not np.all(np.isfinite(X)):
#         raise ValueError(
#             "X contains non-finite values."
#         )

#     if not np.all(np.isfinite(Y)):
#         raise ValueError(
#             "Y contains non-finite values."
#         )

#     if rng is None:
#         rng = np.random.default_rng(42)

#     if bw is None:
#         bx = _bw(
#             X,
#             rng=rng,
#         )

#         by = _bw(
#             Y,
#             rng=rng,
#         )
#     else:
#         bx = float(bw)
#         by = float(bw)

#     H = (
#         np.eye(n)
#         - 1.0 / n
#     )

#     Kc = (
#         H
#         @ _K(X, bx)
#         @ H
#     )

#     Lc = (
#         H
#         @ _K(Y, by)
#         @ H
#     )

#     value = (
#         np.trace(Kc @ Lc)
#         / (n ** 2)
#     )

#     return float(
#         max(value, 0.0)
#     )


# # ============================================================
# # ANM RESIDUALS
# # ============================================================

# def _residuals(
#     cause,
#     effect,
#     n_splits=5,
#     random_state=42,
# ):
#     """
#     Estimate ANM residuals using K-fold cross-fitting.

#     For:

#         cause -> effect

#     fit:

#         effect = g(cause) + U

#     and return:

#         U = effect - g_hat(cause)
#     """
#     cause = np.asarray(
#         cause,
#         dtype=float,
#     )

#     effect = np.asarray(
#         effect,
#         dtype=float,
#     )

#     cause = np.ravel(cause)
#     effect = np.ravel(effect)

#     n = len(cause)

#     if n != len(effect):
#         raise ValueError(
#             "cause and effect must have "
#             "the same length."
#         )

#     if n < n_splits:
#         raise ValueError(
#             f"Number of samples ({n}) must be "
#             f">= n_splits ({n_splits})."
#         )

#     if not np.all(np.isfinite(cause)):
#         raise ValueError(
#             "cause contains non-finite values."
#         )

#     if not np.all(np.isfinite(effect)):
#         raise ValueError(
#             "effect contains non-finite values."
#         )

#     residuals = np.empty(
#         n,
#         dtype=float,
#     )

#     kf = KFold(
#         n_splits=n_splits,
#         shuffle=True,
#         random_state=random_state,
#     )

#     for fold_id, (
#         train_idx,
#         test_idx,
#     ) in enumerate(
#         kf.split(cause)
#     ):

#         gp = GaussianProcessRegressor(
#             kernel=RBF() + WhiteKernel(),
#             alpha=1e-3,
#             normalize_y=True,
#             n_restarts_optimizer=0,
#             random_state=(
#                 int(random_state)
#                 + fold_id
#             ),
#         )

#         gp.fit(
#             cause[train_idx].reshape(-1, 1),
#             effect[train_idx],
#         )

#         predictions = gp.predict(
#             cause[test_idx].reshape(-1, 1)
#         )

#         residuals[test_idx] = (
#             effect[test_idx]
#             - predictions
#         )

#     return residuals


# # ============================================================
# # DAG DISCOVERY
# # ============================================================

# def discover_dag(
#     data,
#     verbose=True,
#     percentile=75,
#     random_state=42,
# ):
#     """
#     Discover a sparse DAG using pairwise ANM + HSIC.

#     Notebook logic:

#         1. Fit Xi -> Xj
#         2. Fit Xj -> Xi
#         3. Compute HSIC(residual, proposed cause)
#         4. Lower HSIC determines candidate direction
#         5. Absolute HSIC difference is confidence
#         6. Keep candidates at or above the configured percentile
#         7. Remove cycles by removing the weakest-confidence edge
#            from each detected cycle
#         8. Return adjacency matrix and topological order

#     Parameters
#     ----------
#     data : array-like
#         Shape (n_samples, n_features).

#     verbose : bool, default=True
#         Print DAG discovery diagnostics.

#     percentile : float, default=75
#         Percentile used for confidence thresholding.

#     random_state : int, default=42
#         Local deterministic random seed.

#     Returns
#     -------
#     adj : np.ndarray
#         Binary adjacency matrix.

#     order : list
#         Topological ordering of the discovered DAG.
#     """
#     import networkx as nx

#     data = np.asarray(
#         data,
#         dtype=float,
#     )

#     if data.ndim != 2:
#         raise ValueError(
#             "data must be a 2D array "
#             "(n_samples, n_features)."
#         )

#     n, p = data.shape

#     if n < 2:
#         raise ValueError(
#             "data must contain at least "
#             "2 samples."
#         )

#     if p < 1:
#         raise ValueError(
#             "data must contain at least "
#             "1 feature."
#         )

#     if not np.all(np.isfinite(data)):
#         raise ValueError(
#             "data contains non-finite values."
#         )

#     percentile = float(percentile)

#     if not 0.0 <= percentile <= 100.0:
#         raise ValueError(
#             "percentile must be between "
#             "0 and 100."
#         )

#     random_state = int(
#         random_state
#     )

#     # --------------------------------------------------------
#     # Local RNG
#     # --------------------------------------------------------

#     rng = np.random.default_rng(
#         random_state
#     )

#     # --------------------------------------------------------
#     # Storage
#     # --------------------------------------------------------

#     adj = np.zeros(
#         (p, p),
#         dtype=int,
#     )

#     hsic_diffs = []

#     edge_candidates = []

#     if verbose:
#         print(
#             f"  DAG discovery: "
#             f"{p} vars, "
#             f"{p * (p - 1) // 2} pairs..."
#         )

#     # --------------------------------------------------------
#     # Pairwise ANM orientation
#     # --------------------------------------------------------

#     for pair_id, (
#         i,
#         j,
#     ) in enumerate(
#         combinations(
#             range(p),
#             2,
#         )
#     ):

#         # ----------------------------------------------------
#         # Deterministic local sample
#         # ----------------------------------------------------

#         pair_rng = np.random.default_rng(
#             random_state
#             + pair_id
#         )

#         idx = pair_rng.choice(
#             n,
#             min(n, 500),
#             replace=False,
#         )

#         # ----------------------------------------------------
#         # Forward: Xi -> Xj
#         # ----------------------------------------------------

#         Rf = _residuals(
#             data[idx, i],
#             data[idx, j],
#             random_state=(
#                 random_state
#                 + pair_id * 2
#             ),
#         )

#         # ----------------------------------------------------
#         # Reverse: Xj -> Xi
#         # ----------------------------------------------------

#         Rr = _residuals(
#             data[idx, j],
#             data[idx, i],
#             random_state=(
#                 random_state
#                 + pair_id * 2
#                 + 1
#             ),
#         )

#         # ----------------------------------------------------
#         # HSIC
#         # ----------------------------------------------------

#         hf = hsic(
#             Rf,
#             data[idx, i],
#             rng=np.random.default_rng(
#                 random_state
#                 + pair_id * 3
#             ),
#         )

#         hr = hsic(
#             Rr,
#             data[idx, j],
#             rng=np.random.default_rng(
#                 random_state
#                 + pair_id * 3
#                 + 1
#             ),
#         )

#         # ----------------------------------------------------
#         # Confidence
#         # ----------------------------------------------------

#         diff = abs(
#             hf - hr
#         )

#         hsic_diffs.append(
#             float(diff)
#         )

#         # ----------------------------------------------------
#         # Candidate orientation
#         # ----------------------------------------------------

#         if hf < hr:

#             edge_candidates.append(
#                 (
#                     i,
#                     j,
#                     float(diff),
#                 )
#             )

#             direction = (
#                 f"X{i + 1}→X{j + 1}"
#             )

#         else:

#             edge_candidates.append(
#                 (
#                     j,
#                     i,
#                     float(diff),
#                 )
#             )

#             direction = (
#                 f"X{j + 1}→X{i + 1}"
#             )

#         if verbose:
#             print(
#                 f"    {direction}  "
#                 f"HSIC("
#                 f"fwd={hf:.5f}, "
#                 f"rev={hr:.5f}"
#                 f")"
#             )

#     # --------------------------------------------------------
#     # Dynamic confidence threshold
#     # --------------------------------------------------------

#     if len(hsic_diffs) == 0:

#         threshold = 0.0

#     else:

#         threshold = np.percentile(
#             hsic_diffs,
#             percentile,
#         )

#     if verbose:
#         print(
#             f"\nEdges before thresholding: "
#             f"{len(edge_candidates)}"
#         )

#         print(
#             "Dynamic HSIC threshold "
#             f"({percentile:g}th percentile): "
#             f"{threshold:.6f}"
#         )

#     # --------------------------------------------------------
#     # Keep high-confidence edges
#     # --------------------------------------------------------

#     for (
#         u,
#         v,
#         confidence,
#     ) in edge_candidates:

#         if confidence >= threshold:

#             adj[u, v] = 1

#     if verbose:
#         print(
#             f"Edges after thresholding: "
#             f"{adj.sum()}"
#         )

#     # --------------------------------------------------------
#     # Remove cycles
#     #
#     # Verified notebook logic:
#     # remove the weakest-confidence edge in a detected cycle.
#     # --------------------------------------------------------

#     confidence_map = {
#         (u, v): confidence
#         for (
#             u,
#             v,
#             confidence,
#         ) in edge_candidates
#     }

#     while True:

#         G = nx.DiGraph()

#         G.add_nodes_from(
#             range(p)
#         )

#         G.add_edges_from(
#             np.argwhere(adj).tolist()
#         )

#         try:

#             cycle = nx.find_cycle(
#                 G,
#                 orientation="original",
#             )

#         except nx.NetworkXNoCycle:

#             break

#         # ----------------------------------------------------
#         # Identify every edge in the detected cycle
#         # ----------------------------------------------------

#         cycle_edges = []

#         for edge in cycle:

#             u = int(edge[0])
#             v = int(edge[1])

#             confidence = confidence_map.get(
#                 (u, v),
#                 0.0,
#             )

#             cycle_edges.append(
#                 (
#                     confidence,
#                     u,
#                     v,
#                 )
#             )

#         # ----------------------------------------------------
#         # Remove weakest-confidence edge
#         # ----------------------------------------------------

#         (
#             weakest_confidence,
#             weakest_u,
#             weakest_v,
#         ) = min(
#             cycle_edges,
#             key=lambda item: (
#                 item[0],
#                 item[1],
#                 item[2],
#             ),
#         )

#         adj[
#             weakest_u,
#             weakest_v,
#         ] = 0

#         if verbose:
#             print(
#                 "    Cycle removed: "
#                 f"X{weakest_u + 1}"
#                 f"→"
#                 f"X{weakest_v + 1} "
#                 f"(confidence="
#                 f"{weakest_confidence:.6f})"
#             )

#     # --------------------------------------------------------
#     # DAG validation
#     # --------------------------------------------------------

#     G = nx.DiGraph()

#     G.add_nodes_from(
#         range(p)
#     )

#     G.add_edges_from(
#         np.argwhere(adj).tolist()
#     )

#     is_dag = (
#         nx.is_directed_acyclic_graph(G)
#     )

#     if not is_dag:
#         raise RuntimeError(
#             "DAG discovery failed to produce "
#             "an acyclic graph."
#         )

#     if verbose:

#         print(
#             f"DAG valid: "
#             f"{is_dag}"
#         )

#         print(
#             f"Edges after cycle removal: "
#             f"{adj.sum()}"
#         )

#     # --------------------------------------------------------
#     # Topological ordering
#     # --------------------------------------------------------

#     order = list(
#         nx.topological_sort(G)
#     )

#     # --------------------------------------------------------
#     # Safety fallback
#     # --------------------------------------------------------

#     for i in range(p):

#         if i not in order:

#             order.append(i)

#     return adj, order


# __all__ = [
#     "hsic",
#     "discover_dag",
# ]

"""HSIC + ANM DAG discovery from the verified notebook."""

from itertools import combinations

import networkx as nx
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel
from sklearn.model_selection import KFold


def _bw(X, rng=None, max_subsample=300):
    if rng is None:
        rng = np.random.default_rng(42)

    X = np.asarray(X, dtype=float)
    X = X.reshape(-1, 1) if X.ndim == 1 else X

    n = len(X)

    if n <= max_subsample:
        idx = np.arange(n)
    else:
        idx = rng.choice(
            n,
            max_subsample,
            replace=False,
        )

    distances = np.sqrt(
        (
            (
                X[idx, None]
                - X[None, idx, :]
            ) ** 2
        ).sum(-1)
    )

    positive = distances[distances > 0]
    median = np.median(positive)

    return float(median) if median > 0 else 1.0


def _K(X, bw):
    X = np.asarray(X, dtype=float)
    X = X.reshape(-1, 1) if X.ndim == 1 else X

    return np.exp(
        -(
            (X[:, None] - X[None, :]) ** 2
        ).sum(-1)
        / (2 * bw ** 2)
    )


def hsic(X, Y, bw=None, rng=None):
    bx = bw or _bw(X, rng=rng)
    by = bw or _bw(Y, rng=rng)

    n = len(X)
    H = np.eye(n) - (1.0 / n)

    Kc = H @ _K(X, bx) @ H
    Lc = H @ _K(Y, by) @ H

    return float(
        np.trace(Kc @ Lc)
    ) / (n ** 2)


def _residuals(
    cause,
    effect,
    n_splits=5,
    random_state=42,
):
    cause = np.asarray(cause, dtype=float)
    effect = np.asarray(effect, dtype=float)

    if cause.ndim != 1 or effect.ndim != 1:
        raise ValueError(
            "cause and effect must be 1D scalar arrays"
        )

    if len(cause) != len(effect):
        raise ValueError(
            "cause and effect must have the same length"
        )

    if len(cause) < n_splits:
        raise ValueError(
            f"Number of samples ({len(cause)}) must be >= "
            f"n_splits ({n_splits})"
        )

    if (
        not np.all(np.isfinite(cause))
        or not np.all(np.isfinite(effect))
    ):
        raise ValueError(
            "Input arrays must contain finite values "
            "(no NaN or Inf)"
        )

    if (
        np.isclose(np.std(cause), 0.0)
        or np.isclose(np.std(effect), 0.0)
    ):
        raise ValueError(
            "Input arrays must have non-zero variance"
        )

    residuals = np.empty(len(cause))

    kf = KFold(
        n_splits=n_splits,
        shuffle=True,
        random_state=random_state,
    )

    for train_idx, test_idx in kf.split(cause):
        gp = GaussianProcessRegressor(
            kernel=RBF() + WhiteKernel(),
            alpha=1e-3,
            normalize_y=True,
            n_restarts_optimizer=0,
            random_state=random_state,
        )

        gp.fit(
            cause[train_idx].reshape(-1, 1),
            effect[train_idx],
        )

        predictions = gp.predict(
            cause[test_idx].reshape(-1, 1)
        )

        residuals[test_idx] = (
            effect[test_idx] - predictions
        )

    return residuals


def discover_dag(
    data,
    verbose=True,
    random_state=42,
    cycle_strategy="weakest",
    percentile=75.0,
):
    """
    Pairwise HSIC + ANM orientation -> sparse DAG + topological order.

    Parameters exactly match the verified notebook.
    """
    data = np.asarray(data, dtype=float)

    if data.ndim != 2:
        raise ValueError(
            "Data must be a 2D matrix of shape "
            "(n_samples, n_features)"
        )

    if not np.all(np.isfinite(data)):
        raise ValueError(
            "Data contains non-finite values"
        )

    if not (0.0 <= percentile <= 100.0):
        raise ValueError(
            "percentile must be between 0.0 and 100.0"
        )

    for col in range(data.shape[1]):
        if np.isclose(
            np.std(data[:, col]),
            0.0,
        ):
            raise ValueError(
                f"Feature column {col} has zero variance"
            )

    rng = np.random.default_rng(
        random_state
    )

    n, p = data.shape

    adj = np.zeros(
        (p, p),
        dtype=int,
    )

    hsic_diffs = []
    edge_candidates = []

    if verbose:
        print(
            f"  DAG discovery: {p} vars, "
            f"{p * (p - 1) // 2} pairs..."
        )

    for i, j in combinations(
        range(p),
        2,
    ):
        idx = rng.choice(
            n,
            min(n, 500),
            replace=False,
        )

        residual_forward = _residuals(
            data[idx, i],
            data[idx, j],
            random_state=random_state,
        )

        residual_reverse = _residuals(
            data[idx, j],
            data[idx, i],
            random_state=random_state,
        )

        hsic_forward = hsic(
            residual_forward,
            data[idx, i],
            rng=rng,
        )

        hsic_reverse = hsic(
            residual_reverse,
            data[idx, j],
            rng=rng,
        )

        diff = abs(
            hsic_forward - hsic_reverse
        )

        hsic_diffs.append(diff)

        if hsic_forward < hsic_reverse:
            cause, effect = i, j
            direction = f"X{i + 1}->X{j + 1}"
        else:
            cause, effect = j, i
            direction = f"X{j + 1}->X{i + 1}"

        edge_candidates.append(
            (cause, effect, diff)
        )

        if verbose:
            print(
                f"    {direction}  "
                f"HSIC(fwd={hsic_forward:.5f}, "
                f"rev={hsic_reverse:.5f})  "
                f"diff={diff:.6f}"
            )

    if len(hsic_diffs) == 0:
        raise ValueError(
            "No pairwise confidence values could be computed"
        )

    threshold = float(
        np.percentile(
            hsic_diffs,
            percentile,
        )
    )

    if verbose:
        print(
            f"\nEdges before thresholding: "
            f"{len(edge_candidates)}"
        )
        print(
            f"Dynamic HSIC threshold "
            f"({percentile}th percentile): "
            f"{threshold:.6f}"
        )

    edge_conf = {}

    for cause, effect, confidence in edge_candidates:
        if confidence >= threshold:
            adj[cause, effect] = 1
            edge_conf[(cause, effect)] = confidence

    if verbose:
        print(
            f"Edges after thresholding: "
            f"{adj.sum()}"
        )

    cycles_removed = 0

    while True:
        G = nx.DiGraph(
            np.argwhere(adj).tolist()
        )

        try:
            cycle = nx.find_cycle(G)
            cycles_removed += 1

            if cycle_strategy == "weakest":
                cycle_edges = [
                    (
                        (u, v),
                        edge_conf.get(
                            (u, v),
                            0.0,
                        ),
                    )
                    for u, v in cycle
                ]

                edge_to_remove, _ = min(
                    cycle_edges,
                    key=lambda item: (
                        item[1],
                        item[0],
                    ),
                )

                adj[
                    edge_to_remove[0],
                    edge_to_remove[1],
                ] = 0

                edge_conf.pop(
                    edge_to_remove,
                    None,
                )
            else:
                u, v = cycle[0]
                adj[u, v] = 0

        except nx.NetworkXNoCycle:
            break

    G = nx.DiGraph(
        np.argwhere(adj).tolist()
    )

    is_dag = nx.is_directed_acyclic_graph(G)

    if verbose:
        print(
            f"DAG valid: {is_dag} "
            f"(cycles removed: {cycles_removed})"
        )

        if cycles_removed == 0:
            print(
                "Note: Graph was naturally acyclic "
                "at this threshold (0 cycles detected)."
            )

        print(
            f"Edges after cycle removal: "
            f"{adj.sum()}"
        )

    in_degree = adj.sum(axis=0)

    queue = [
        i
        for i in range(p)
        if in_degree[i] == 0
    ]

    order = []

    while queue:
        v = queue.pop(0)
        order.append(v)

        for j in range(p):
            if adj[v, j]:
                in_degree[j] -= 1

                if in_degree[j] == 0:
                    queue.append(j)

    for i in range(p):
        if i not in order:
            order.append(i)

    return adj, order


__all__ = [
    "hsic",
    "discover_dag",
]
