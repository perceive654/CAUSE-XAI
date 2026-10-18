
# # import numpy as np

# # from scipy.stats import laplace as sp_laplace
# # from sklearn.gaussian_process import GaussianProcessRegressor
# # from sklearn.gaussian_process.kernels import RBF, WhiteKernel
# # from sklearn.preprocessing import StandardScaler


# # class _StructEq:
# #     """
# #     GP-based structural equation:

# #         X_j = g_j(Pa(j)) + U_j
# #     """

# #     def __init__(self, j, parents):
# #         self.j = j
# #         self.parents = parents

# #         self.is_root = len(parents) == 0

# #         self.gp = None
# #         self.sc = StandardScaler()

# #     def fit(self, data):
# #         """
# #         Fit the structural mechanism for variable j.

# #         Returns
# #         -------
# #         residuals : np.ndarray
# #             X_j - g_j(Pa(j))
# #         """

# #         Xj = data[:, self.j]

# #         # ---------------------------------------------------------
# #         # Root variable
# #         # ---------------------------------------------------------
# #         if self.is_root:
# #             return Xj

# #         # ---------------------------------------------------------
# #         # Parent variables
# #         # ---------------------------------------------------------
# #         Pa = data[:, self.parents]

# #         Ps = self.sc.fit_transform(Pa)

# #         # ---------------------------------------------------------
# #         # Gaussian Process mechanism
# #         # ---------------------------------------------------------
# #         gp = GaussianProcessRegressor(
# #             kernel=RBF() + WhiteKernel(),
# #             alpha=1e-4,
# #             normalize_y=True,
# #             n_restarts_optimizer=0,
# #         )

# #         # Same restricted fitting strategy as notebook
# #         n = len(Ps)

# #         idx = np.random.choice(
# #             n,
# #             min(n, 400),
# #             replace=False
# #         )

# #         gp.fit(
# #             Ps[idx],
# #             Xj[idx]
# #         )

# #         self.gp = gp

# #         # ---------------------------------------------------------
# #         # Structural residual
# #         # ---------------------------------------------------------
# #         prediction = gp.predict(Ps)

# #         residuals = Xj - prediction

# #         return residuals

# #     def predict(self, pa):
# #         """
# #         Predict g_j(Pa).
# #         """

# #         if self.is_root:

# #             if np.ndim(pa) > 1:
# #                 return np.zeros(pa.shape[0])

# #             return np.zeros(1)

# #         pa = np.asarray(pa)

# #         if pa.ndim == 1:
# #             pa = pa.reshape(1, -1)

# #         return self.gp.predict(
# #             self.sc.transform(pa)
# #         )

        


# # class ANM:
# #     """
# #     Additive Noise Model — causal backbone of CCE-ANM.

# #     Structural equation:

# #         X_j = g_j(Pa(j)) + U_j

# #     where:

# #         g_j = GP-based causal mechanism
# #         U_j = Laplace-distributed noise

# #     Methods
# #     -------
# #     fit(data)
# #         Learn structural equations and noise distributions.

# #     forward(u)
# #         Map latent noise u -> observed feature space x.

# #     inverse(x)
# #         Recover latent noise from observation.

# #     do_sample(fixed, K)
# #         Generate interventional samples.

# #     violation(x)
# #         Compute causal-manifold violation.

# #     violation_details(x)
# #         Compute feature-level violation diagnostics.

# #     noise_nll(x)
# #         Compute negative log-likelihood of implied noise.
# #     """

# #     def __init__(
# #         self,
# #         adj,
# #         order,
# #         feature_names=None
# #     ):
# #         self.adj = np.asarray(adj)
# #         self.order = list(order)

# #         self.p = self.adj.shape[0]

# #         # ---------------------------------------------------------
# #         # Feature names are ONLY for display.
# #         # They do not affect ANM computation.
# #         # ---------------------------------------------------------
# #         self.feature_names = (
# #             list(feature_names)
# #             if feature_names is not None
# #             else [f"X{i + 1}" for i in range(self.p)]
# #         )

# #         if len(self.feature_names) != self.p:
# #             raise ValueError(
# #                 "feature_names must have the same length "
# #                 "as the number of features."
# #             )

# #         self.eqs = {}
# #         self.noise = {}
# #         self.residual_std = {}

# #         self._ok = False

# #     # =========================================================
# #     # FIT
# #     # =========================================================

# #     def fit(
# #         self,
# #         data,
# #         verbose=True
# #     ):
# #         """
# #         Fit all structural equations and their
# #         Laplace noise distributions.

# #         This follows the notebook ANM logic exactly.
# #         """

# #         data = np.asarray(
# #             data,
# #             dtype=float
# #         )

# #         if data.ndim != 2:
# #             raise ValueError(
# #                 "data must be a 2D array of shape "
# #                 "(n_samples, n_features)"
# #             )

# #         if data.shape[1] != self.p:
# #             raise ValueError(
# #                 f"Expected {self.p} features, "
# #                 f"got {data.shape[1]}"
# #             )

# #         # ---------------------------------------------------------
# #         # Fit each structural equation in topological order
# #         # ---------------------------------------------------------

# #         for j in self.order:

# #             # Parents of X_j
# #             pa = [
# #                 i
# #                 for i in range(self.p)
# #                 if self.adj[i, j]
# #             ]

# #             # Structural equation
# #             eq = _StructEq(
# #                 j=j,
# #                 parents=pa
# #             )

# #             # Structural residuals
# #             R = eq.fit(data)

# #             # -----------------------------------------------------
# #             # Fit Laplace noise distribution
# #             # -----------------------------------------------------

# #             loc, scale = sp_laplace.fit(R)

# #             # Store structural equation
# #             self.eqs[j] = eq

# #             # Store noise parameters
# #             self.noise[j] = (
# #                 float(loc),
# #                 float(scale)
# #             )

# #             # Actual residual standard deviation
# #             self.residual_std[j] = float(
# #                 np.std(R)
# #             )

# #             # -----------------------------------------------------
# #             # Notebook-style display
# #             # -----------------------------------------------------

# #             if verbose:

# #                 if self.feature_names is not None:
# #                     variable = self.feature_names[j]
# #                     parent_names = [
# #                         self.feature_names[i]
# #                         for i in pa
# #                     ]
# #                 else:
# #                     variable = f"X{j + 1}"
# #                     parent_names = [
# #                         f"X{i + 1}"
# #                         for i in pa
# #                     ]

# #                 print(
# #                     f"  {variable}: "
# #                     f"pa={parent_names}  "
# #                     f"Laplace("
# #                     f"loc={loc:.3f}, "
# #                     f"scale={scale:.3f})  "
# #                     f"residual_std="
# #                     f"{self.residual_std[j]:.3f}"
# #                 )

# #         self._ok = True

# #         return self

# #     # =========================================================
# #     # FORWARD
# #     # =========================================================

# #     def forward(self, u):
# #         """
# #         Φ: R^p -> X_M

# #         Generate a causal-valid feature vector from
# #         latent noise variables.
# #         """

# #         u = np.asarray(
# #             u,
# #             dtype=float
# #         )

# #         batch = u.ndim == 2

# #         if not batch:
# #             u = u[None, :]

# #         x = np.zeros_like(u)

# #         for j in self.order:

# #             eq = self.eqs[j]

# #             if eq.is_root:

# #                 g = np.zeros(
# #                     len(u)
# #                 )

# #             else:

# #                 g = eq.predict(
# #                     x[:, eq.parents]
# #                 )

# #             x[:, j] = (
# #                 g +
# #                 u[:, j]
# #             )

# #         return (
# #             x
# #             if batch
# #             else x[0]
# #         )

# #     # =========================================================
# #     # INVERSE
# #     # =========================================================

# #     def inverse(self, x):
# #         """
# #         Φ⁻¹: X_M -> R^p

# #         Recover the implied noise:

# #             U_j = X_j - g_j(Pa(j))
# #         """

# #         x = np.asarray(
# #             x,
# #             dtype=float
# #         )

# #         batch = x.ndim == 2

# #         if not batch:
# #             x = x[None, :]

# #         u = np.zeros_like(x)

# #         for j in self.order:

# #             eq = self.eqs[j]

# #             if eq.is_root:

# #                 g = np.zeros(
# #                     len(x)
# #                 )

# #             else:

# #                 g = eq.predict(
# #                     x[:, eq.parents]
# #                 )

# #             u[:, j] = (
# #                 x[:, j] -
# #                 g
# #             )

# #         return (
# #             u
# #             if batch
# #             else u[0]
# #         )

# #     # =========================================================
# #     # DO SAMPLE
# #     # =========================================================

# #     def do_sample(
# #         self,
# #         fixed,
# #         K=100
# #     ):
# #         """
# #         Sample from:

# #             P_M(X | do(X_S = x_S))

# #         fixed:
# #             {feature_index: intervention_value}

# #         Intervened variables are fixed and their
# #         incoming causal mechanism is severed.
# #         """

# #         S = set(
# #             fixed.keys()
# #         )

# #         samp = np.zeros(
# #             (K, self.p)
# #         )

# #         for j in self.order:

# #             # -------------------------------------------------
# #             # Intervention
# #             # -------------------------------------------------

# #             if j in S:

# #                 samp[:, j] = fixed[j]

# #                 continue

# #             eq = self.eqs[j]

# #             loc, scale = self.noise[j]

# #             # -------------------------------------------------
# #             # Structural mechanism
# #             # -------------------------------------------------

# #             if eq.is_root:

# #                 g = np.zeros(K)

# #             else:

# #                 g = eq.predict(
# #                     samp[:, eq.parents]
# #                 )

# #             # -------------------------------------------------
# #             # Add ANM noise
# #             # -------------------------------------------------

# #             samp[:, j] = (
# #                 g +
# #                 sp_laplace.rvs(
# #                     loc=loc,
# #                     scale=scale,
# #                     size=K
# #                 )
# #             )

# #         return samp

# #     # =========================================================
# #     # VIOLATION
# #     # =========================================================

# #     def violation(self, x):
# #         """
# #         Compute the causal-manifold violation score:

# #             V_M(x)
# #               = mean_j(
# #                     |R_j - loc_j|
# #                     /
# #                     (sqrt(2) * scale_j)
# #                 )

# #         This is the same heuristic used by the notebook.
# #         """

# #         x = np.asarray(
# #             x,
# #             dtype=float
# #         )

# #         x = np.atleast_1d(x)

# #         vals = []

# #         for j in self.order:

# #             eq = self.eqs[j]

# #             loc, scale = self.noise[j]

# #             if eq.is_root:

# #                 Rj = (
# #                     x[j] -
# #                     loc
# #                 )

# #             else:

# #                 Rj = (
# #                     x[j] -
# #                     eq.predict(
# #                         x[eq.parents]
# #                     )[0] -
# #                     loc
# #                 )

# #             vals.append(
# #                 abs(Rj) /
# #                 (
# #                     np.sqrt(2.0) *
# #                     scale +
# #                     1e-8
# #                 )
# #             )

# #         return float(
# #             np.mean(vals)
# #         )

# #     # =========================================================
# #     # VIOLATION DETAILS
# #     # =========================================================

# #     def violation_details(self, x):
# #         """
# #         Return per-feature ANM violation diagnostics.
# #         """

# #         x = np.asarray(
# #             x,
# #             dtype=float
# #         )

# #         x = np.atleast_1d(x)

# #         residuals = {}
# #         standardized = {}

# #         for j in self.order:

# #             eq = self.eqs[j]

# #             loc, scale = self.noise[j]

# #             if eq.is_root:

# #                 g_value = 0.0

# #             else:

# #                 parents = (
# #                     x[eq.parents]
# #                     .reshape(1, -1)
# #                 )

# #                 g_value = eq.predict(
# #                     parents
# #                 )[0]

# #             noise_value = (
# #                 x[j] -
# #                 g_value
# #             )

# #             residual = (
# #                 noise_value -
# #                 loc
# #             )

# #             z = (
# #                 abs(residual) /
# #                 (
# #                     np.sqrt(2.0) *
# #                     scale +
# #                     1e-8
# #                 )
# #             )

# #             residuals[int(j)] = float(
# #                 residual
# #             )

# #             standardized[int(j)] = float(
# #                 z
# #             )

# #         z_values = np.array(
# #             list(
# #                 standardized.values()
# #             )
# #         )

# #         feature_indices = list(
# #             standardized.keys()
# #         )

# #         worst_feature = feature_indices[
# #             int(
# #                 np.argmax(z_values)
# #             )
# #         ]

# #         return {
# #             "residuals": residuals,

# #             "standardized": standardized,

# #             "mean": float(
# #                 np.mean(z_values)
# #             ),

# #             "median": float(
# #                 np.median(z_values)
# #             ),

# #             "p95": float(
# #                 np.percentile(
# #                     z_values,
# #                     95
# #                 )
# #             ),

# #             "maximum": float(
# #                 np.max(z_values)
# #             ),

# #             "worst_feature": int(
# #                 worst_feature
# #             ),

# #             "worst_feature_name":
# #                 self.feature_names[
# #                     worst_feature
# #                 ],
# #         }

# #     # =========================================================
# #     # NOISE NLL
# #     # =========================================================

# #     def noise_nll(self, x):
# #         """
# #         Return total negative log-likelihood of
# #         the implied ANM noise.
# #         """

# #         x = np.asarray(
# #             x,
# #             dtype=float
# #         )

# #         total_nll = 0.0

# #         noise_values = []

# #         for j in self.order:

# #             eq = self.eqs[j]

# #             loc, scale = self.noise[j]

# #             if eq.is_root:

# #                 g_value = 0.0

# #             else:

# #                 parents = (
# #                     x[eq.parents]
# #                     .reshape(1, -1)
# #                 )

# #                 g_value = eq.predict(
# #                     parents
# #                 )[0]

# #             u_value = (
# #                 x[j] -
# #                 g_value
# #             )

# #             total_nll -= sp_laplace.logpdf(
# #                 u_value,
# #                 loc=loc,
# #                 scale=scale
# #             )

# #             noise_values.append(
# #                 u_value
# #             )

# #         return {
# #             "nll": float(
# #                 total_nll
# #             ),

# #             "noise_values":
# #                 np.asarray(
# #                     noise_values
# #                 ),
# #         }

# import numpy as np

# from scipy.stats import laplace as sp_laplace
# from sklearn.gaussian_process import GaussianProcessRegressor
# from sklearn.gaussian_process.kernels import RBF, WhiteKernel
# from sklearn.preprocessing import StandardScaler


# class _StructEq:
#     """
#     GP-based structural equation:

#         X_j = g_j(Pa(j)) + U_j

#     The implementation follows the verified notebook ANM logic.
#     """

#     def __init__(self, j, parents, random_state=42):
#         self.j = int(j)
#         self.parents = list(parents)
#         self.is_root = len(self.parents) == 0

#         self.gp = None
#         self.sc = StandardScaler()

#         # Local seed for deterministic mechanism fitting.
#         self.random_state = int(random_state)

#     def fit(self, data):
#         """
#         Fit the structural mechanism for variable j.

#         Returns
#         -------
#         residuals : np.ndarray
#             Structural residuals X_j - g_j(Pa(j)).
#         """
#         data = np.asarray(data, dtype=float)

#         Xj = data[:, self.j]

#         # Root variable:
#         # X_j = U_j, so the observed values are the residuals.
#         if self.is_root:
#             return Xj

#         # Parent variables.
#         Pa = data[:, self.parents]
#         Ps = self.sc.fit_transform(Pa)

#         # Gaussian-process structural mechanism.
#         gp = GaussianProcessRegressor(
#             kernel=RBF() + WhiteKernel(),
#             alpha=1e-4,
#             normalize_y=True,
#             n_restarts_optimizer=0,
#             random_state=self.random_state,
#         )

#         # Same restricted fitting strategy as the verified notebook.
#         n = len(Ps)

#         rng = np.random.default_rng(
#             self.random_state + self.j
#         )

#         idx = rng.choice(
#             n,
#             min(n, 400),
#             replace=False,
#         )

#         gp.fit(
#             Ps[idx],
#             Xj[idx],
#         )

#         self.gp = gp

#         # Structural residuals.
#         prediction = gp.predict(Ps)

#         residuals = Xj - prediction

#         return residuals

#     def predict(self, pa):
#         """
#         Predict g_j(Pa).
#         """
#         if self.is_root:
#             pa = np.asarray(pa)

#             if pa.ndim > 1:
#                 return np.zeros(
#                     pa.shape[0],
#                     dtype=float,
#                 )

#             return np.zeros(
#                 1,
#                 dtype=float,
#             )

#         pa = np.asarray(
#             pa,
#             dtype=float,
#         )

#         if pa.ndim == 1:
#             pa = pa.reshape(1, -1)

#         return self.gp.predict(
#             self.sc.transform(pa)
#         )


# class ANM:
#     """
#     Additive Noise Model — causal backbone of CCE-ANM.

#     Structural equation:

#         X_j = g_j(Pa(j)) + U_j

#     where:

#         g_j = GP-based causal mechanism
#         U_j = Laplace-distributed noise

#     The implementation follows the verified notebook logic, including:

#     - deterministic local RNG isolation
#     - deterministic GP mechanism fitting
#     - CRN-compatible interventional sampling
#     - causal-manifold violation diagnostics
#     - implied-noise negative log-likelihood

#     Feature names are retained only for display compatibility and do not
#     affect ANM computation.
#     """

#     def __init__(
#         self,
#         adj,
#         order,
#         feature_names=None,
#         random_state=42,
#     ):
#         self.adj = np.asarray(
#             adj,
#             dtype=int,
#         )

#         self.order = [
#             int(x)
#             for x in order
#         ]

#         self.p = self.adj.shape[0]

#         # ---------------------------------------------------------
#         # Feature names are ONLY for display.
#         # They do not affect ANM computation.
#         # ---------------------------------------------------------
#         self.feature_names = (
#             list(feature_names)
#             if feature_names is not None
#             else [
#                 f"X{i + 1}"
#                 for i in range(self.p)
#             ]
#         )

#         if len(self.feature_names) != self.p:
#             raise ValueError(
#                 "feature_names must have the same length "
#                 "as the number of features."
#             )

#         self.eqs = {}
#         self.noise = {}
#         self.residual_std = {}

#         # Verified notebook random-state isolation.
#         self.random_state = int(random_state)

#         self._ok = False

#     # =========================================================
#     # FIT
#     # =========================================================

#     def fit(
#         self,
#         data,
#         verbose=True,
#     ):
#         """
#         Fit all structural equations and their Laplace noise
#         distributions.
#         """
#         data = np.asarray(
#             data,
#             dtype=float,
#         )

#         if data.ndim != 2:
#             raise ValueError(
#                 "data must be a 2D array of shape "
#                 "(n_samples, n_features)"
#             )

#         if data.shape[1] != self.p:
#             raise ValueError(
#                 f"Expected {self.p} features, "
#                 f"got {data.shape[1]}"
#             )

#         if not np.all(np.isfinite(data)):
#             raise ValueError(
#                 "data contains non-finite values (NaN or Inf)"
#             )

#         # ---------------------------------------------------------
#         # Fit each structural equation in topological order
#         # ---------------------------------------------------------

#         for j in self.order:

#             # Parents of X_j.
#             pa = [
#                 i
#                 for i in range(self.p)
#                 if self.adj[i, j]
#             ]

#             # Each structural equation receives an isolated
#             # deterministic seed.
#             eq = _StructEq(
#                 j=j,
#                 parents=pa,
#                 random_state=self.random_state + j,
#             )

#             # Structural residuals.
#             R = eq.fit(data)

#             # -----------------------------------------------------
#             # Fit Laplace noise distribution
#             # -----------------------------------------------------

#             loc, scale = sp_laplace.fit(R)

#             # Store structural equation.
#             self.eqs[j] = eq

#             # Store noise parameters.
#             self.noise[j] = (
#                 float(loc),
#                 float(scale),
#             )

#             # Actual residual standard deviation.
#             self.residual_std[j] = float(
#                 np.std(R)
#             )

#             # -----------------------------------------------------
#             # Notebook-style display
#             # -----------------------------------------------------

#             if verbose:

#                 variable = self.feature_names[j]

#                 parent_names = [
#                     self.feature_names[i]
#                     for i in pa
#                 ]

#                 print(
#                     f"  {variable}: "
#                     f"pa={parent_names}  "
#                     f"Laplace("
#                     f"loc={loc:.3f}, "
#                     f"scale={scale:.3f})  "
#                     f"residual_std="
#                     f"{self.residual_std[j]:.3f}"
#                 )

#         self._ok = True

#         return self

#     # =========================================================
#     # FORWARD
#     # =========================================================

#     def forward(self, u):
#         """
#         Phi: R^p -> X_M

#         Generate a causal-valid feature vector from latent
#         noise variables.
#         """
#         u = np.asarray(
#             u,
#             dtype=float,
#         )

#         batch = u.ndim == 2

#         if not batch:
#             u = u[None, :]

#         x = np.zeros_like(u)

#         for j in self.order:

#             eq = self.eqs[j]

#             if eq.is_root:

#                 g = np.zeros(
#                     len(u),
#                     dtype=float,
#                 )

#             else:

#                 g = eq.predict(
#                     x[:, eq.parents]
#                 )

#             x[:, j] = (
#                 g
#                 + u[:, j]
#             )

#         return (
#             x
#             if batch
#             else x[0]
#         )

#     # =========================================================
#     # INVERSE
#     # =========================================================

#     def inverse(self, x):
#         """
#         Phi^-1: X_M -> R^p

#         Recover the implied structural noise:

#             U_j = X_j - g_j(Pa(j))
#         """
#         x = np.asarray(
#             x,
#             dtype=float,
#         )

#         batch = x.ndim == 2

#         if not batch:
#             x = x[None, :]

#         u = np.zeros_like(x)

#         for j in self.order:

#             eq = self.eqs[j]

#             if eq.is_root:

#                 g = np.zeros(
#                     len(x),
#                     dtype=float,
#                 )

#             else:

#                 g = eq.predict(
#                     x[:, eq.parents]
#                 )

#             u[:, j] = (
#                 x[:, j]
#                 - g
#             )

#         return (
#             u
#             if batch
#             else u[0]
#         )

#     # =========================================================
#     # DO SAMPLE
#     # =========================================================

#     def do_sample(
#         self,
#         fixed,
#         K=100,
#         rng=None,
#         u_noise=None,
#     ):
#         """
#         Sample from:

#             P_M(X | do(X_S = x_S))

#         Parameters
#         ----------
#         fixed : dict
#             {feature_index: intervention_value}

#         K : int, default=100
#             Number of interventional samples.

#         rng : np.random.Generator, optional
#             Local RNG used when u_noise is not supplied.

#         u_noise : np.ndarray, optional
#             Pre-drawn exogenous noise matrix of shape (K, p).

#             When supplied, the same noise realization can be reused
#             across baseline and intervention samples, providing the
#             Common Random Numbers (CRN) mechanism used by the
#             verified notebook.

#         Intervened variables are fixed and their incoming causal
#         mechanism is severed.
#         """

#         S = {
#             int(k): float(v)
#             for k, v in fixed.items()
#         }

#         # ---------------------------------------------------------
#         # CRN mode
#         # ---------------------------------------------------------

#         # if u_noise is not None:

#         #     u_noise = np.asarray(
#         #         u_noise,
#         #         dtype=float,
#         #     )

#         #     K = u_noise.shape[0]
        
#         if u_noise is not None:

#             if isinstance(u_noise, dict):

#                 if len(u_noise) != self.p:
#                     missing = [
#                         j for j in range(self.p)
#                         if j not in u_noise
#                     ]
#                     raise ValueError(
#                         "u_noise dictionary must contain one "
#                         f"noise vector for every feature. Missing: {missing}"
#                     )

#                 noise_by_node = {
#                     int(j): np.asarray(
#                         value,
#                         dtype=float,
#                     ).reshape(-1)
#                     for j, value in u_noise.items()
#                 }

#                 lengths = {
#                     len(values)
#                     for values in noise_by_node.values()
#                 }

#                 if len(lengths) != 1:
#                     raise ValueError(
#                         "All u_noise vectors must have the same length."
#                     )

#                 K = int(next(iter(lengths)))

#                 if K <= 0:
#                     raise ValueError(
#                         "u_noise vectors must contain at least one sample."
#                     )

#                 for j, values in noise_by_node.items():
#                     if not np.all(np.isfinite(values)):
#                         raise ValueError(
#                             f"u_noise[{j}] contains non-finite values."
#                         )

#             else:

#                 u_noise = np.asarray(
#                     u_noise,
#                     dtype=float,
#                 )

#                 if u_noise.ndim != 2:
#                     raise ValueError(
#                         "u_noise array must have shape (K, p)."
#                     )

#                 if u_noise.shape[1] != self.p:
#                     raise ValueError(
#                         f"u_noise must have {self.p} columns; "
#                         f"got {u_noise.shape[1]}."
#                     )

#                 K = u_noise.shape[0]

#                 if K <= 0:
#                     raise ValueError(
#                         "u_noise must contain at least one sample."
#                     )

#                 if not np.all(np.isfinite(u_noise)):
#                     raise ValueError(
#                         "u_noise contains non-finite values."
#                     )

#                 noise_by_node = None

#             # ---------------------------------------------------------
#         # Normal isolated-RNG mode
#         # ---------------------------------------------------------

#         elif rng is None:

#             rng = np.random.default_rng(
#                 self.random_state
#             )

#         samp = np.zeros(
#             (K, self.p),
#             dtype=float,
#         )

#         for j in self.order:

#             # -----------------------------------------------------
#             # Intervention
#             # -----------------------------------------------------

#             if j in S:

#                 samp[:, j] = S[j]

#                 continue

#             eq = self.eqs[j]

#             # -----------------------------------------------------
#             # Structural mechanism
#             # -----------------------------------------------------

#             if eq.is_root:

#                 g = np.zeros(
#                     K,
#                     dtype=float,
#                 )

#             else:

#                 g = eq.predict(
#                     samp[:, eq.parents]
#                 )

#             # -----------------------------------------------------
#             # ANM noise
#             # -----------------------------------------------------

#             if u_noise is not None:

#                 if noise_by_node is not None:
#                     noise_draw = noise_by_node[j]
#                 else:
#                     noise_draw = u_noise[:, j]

#             else:

#                 loc, sc = self.noise[j]

#                 noise_draw = rng.laplace(
#                     loc=loc,
#                     scale=sc,
#                     size=K,
#                 )

#             samp[:, j] = (
#                 g
#                 + noise_draw
#             )

#         return samp

#     # =========================================================
#     # VIOLATION
#     # =========================================================

#     def violation(self, x):
#         """
#         Compute the causal-manifold violation score:

#             V_M(x)
#               = mean_j(
#                     |R_j - loc_j|
#                     /
#                     (sqrt(2) * scale_j)
#                 )
#         """
#         x = np.asarray(
#             x,
#             dtype=float,
#         )

#         x = np.atleast_1d(x)

#         vals = []

#         for j in self.order:

#             eq = self.eqs[j]

#             loc, scale = self.noise[j]

#             if eq.is_root:

#                 Rj = (
#                     x[j]
#                     - loc
#                 )

#             else:

#                 Rj = (
#                     x[j]
#                     - eq.predict(
#                         x[eq.parents]
#                     )[0]
#                     - loc
#                 )

#             vals.append(
#                 abs(Rj)
#                 /
#                 (
#                     np.sqrt(2.0)
#                     * scale
#                     + 1e-8
#                 )
#             )

#         return float(
#             np.mean(vals)
#         )

#     # =========================================================
#     # VIOLATION DETAILS
#     # =========================================================

#     def violation_details(self, x):
#         """
#         Return per-feature ANM violation diagnostics.
#         """
#         x = np.asarray(
#             x,
#             dtype=float,
#         )

#         x = np.atleast_1d(x)

#         residuals = {}
#         standardized = {}

#         for j in self.order:

#             eq = self.eqs[j]

#             loc, scale = self.noise[j]

#             if eq.is_root:

#                 g_value = 0.0

#             else:

#                 parents = (
#                     x[eq.parents]
#                     .reshape(1, -1)
#                 )

#                 g_value = eq.predict(
#                     parents
#                 )[0]

#             noise_value = (
#                 x[j]
#                 - g_value
#             )

#             residual = (
#                 noise_value
#                 - loc
#             )

#             z = (
#                 abs(residual)
#                 /
#                 (
#                     np.sqrt(2.0)
#                     * scale
#                     + 1e-8
#                 )
#             )

#             residuals[int(j)] = float(
#                 residual
#             )

#             standardized[int(j)] = float(
#                 z
#             )

#         z_values = np.array(
#             list(
#                 standardized.values()
#             )
#         )

#         feature_indices = list(
#             standardized.keys()
#         )

#         worst_feature = feature_indices[
#             int(
#                 np.argmax(z_values)
#             )
#         ]

#         return {
#             "residuals": residuals,

#             "standardized": standardized,

#             "mean": float(
#                 np.mean(z_values)
#             ),

#             "median": float(
#                 np.median(z_values)
#             ),

#             "p95": float(
#                 np.percentile(
#                     z_values,
#                     95,
#                 )
#             ),

#             "maximum": float(
#                 np.max(z_values)
#             ),

#             "worst_feature": int(
#                 worst_feature
#             ),

#             "worst_feature_name":
#                 self.feature_names[
#                     worst_feature
#                 ],
#         }

#     # =========================================================
#     # NOISE NLL
#     # =========================================================

#     def noise_nll(self, x):
#         """
#         Return total negative log-likelihood of the
#         implied ANM noise.
#         """
#         x = np.asarray(
#             x,
#             dtype=float,
#         )

#         total_nll = 0.0

#         noise_values = []

#         for j in self.order:

#             eq = self.eqs[j]

#             loc, scale = self.noise[j]

#             if eq.is_root:

#                 g_value = 0.0

#             else:

#                 parents = (
#                     x[eq.parents]
#                     .reshape(1, -1)
#                 )

#                 g_value = eq.predict(
#                     parents
#                 )[0]

#             u_value = (
#                 x[j]
#                 - g_value
#             )

#             total_nll -= sp_laplace.logpdf(
#                 u_value,
#                 loc=loc,
#                 scale=scale,
#             )

#             noise_values.append(
#                 u_value
#             )

#         return {
#             "nll": float(
#                 total_nll
#             ),

#             "noise_values":
#                 np.asarray(
#                     noise_values
#                 ),
#         }

"""Additive Noise Model implementation from the verified notebook."""

import numpy as np
import scipy.stats as sp_stats
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel
from sklearn.preprocessing import StandardScaler


class _StructEq:
    """GP-based structural equation: X_j = g_j(Pa(j)) + U_j."""

    def __init__(self, j, parents, random_state=42):
        self.j = int(j)
        self.parents = list(parents)
        self.is_root = len(self.parents) == 0
        self.gp = None
        self.sc = StandardScaler()
        self.random_state = int(random_state)

    def fit(self, data):
        data = np.asarray(data, dtype=float)
        Xj = data[:, self.j]

        if self.is_root:
            return Xj

        Pa = data[:, self.parents]
        Ps = self.sc.fit_transform(Pa)

        gp = GaussianProcessRegressor(
            kernel=RBF() + WhiteKernel(),
            alpha=1e-4,
            normalize_y=True,
            n_restarts_optimizer=0,
            random_state=self.random_state,
        )

        n = len(Ps)
        rng = np.random.default_rng(self.random_state + self.j)
        idx = rng.choice(n, min(n, 400), replace=False)

        gp.fit(Ps[idx], Xj[idx])
        self.gp = gp

        return Xj - gp.predict(Ps)

    def predict(self, pa):
        if self.is_root:
            pa = np.asarray(pa)
            return np.zeros(
                pa.shape[0] if pa.ndim > 1 else 1,
                dtype=float,
            )

        pa = np.asarray(pa, dtype=float)
        if pa.ndim == 1:
            pa = pa.reshape(1, -1)

        return self.gp.predict(self.sc.transform(pa))


class ANM:
    """Additive Noise Model — causal backbone of CCE-ANM."""

    def __init__(self, adj, order, random_state=42):
        self.adj = np.asarray(adj, dtype=int)
        self.order = [int(x) for x in order]
        self.p = self.adj.shape[0]
        self.eqs = {}
        self.noise = {}
        self.random_state = int(random_state)
        self._ok = False

    def fit(self, data, verbose=True):
        data = np.asarray(data, dtype=float)

        for j in self.order:
            parents = [
                i for i in range(self.p)
                if self.adj[i, j]
            ]

            eq = _StructEq(
                j,
                parents,
                random_state=self.random_state + j,
            )

            residuals = eq.fit(data)
            loc, scale = sp_stats.laplace.fit(residuals)

            self.eqs[j] = eq
            self.noise[j] = (
                float(loc),
                float(scale),
            )

            if verbose:
                print(
                    f"  X{j + 1}: "
                    f"pa={[i + 1 for i in parents] or '[]'}  "
                    f"Laplace(loc={loc:.3f}, scale={scale:.3f})  "
                    f"residual_std={residuals.std():.3f}"
                )

        self._ok = True
        return self

    def forward(self, u):
        """Phi: R^p -> X_M."""
        u = np.asarray(u, dtype=float)
        is_batch = u.ndim == 2
        u = u[None, :] if not is_batch else u

        x = np.zeros_like(u)

        for j in self.order:
            eq = self.eqs[j]
            x[:, j] = (
                eq.predict(x[:, eq.parents])
                if not eq.is_root
                else np.zeros(len(u))
            ) + u[:, j]

        return x if is_batch else x[0]

    def inverse(self, x):
        """Phi^-1: X_M -> R^p."""
        x = np.asarray(x, dtype=float)
        is_batch = x.ndim == 2
        x = x[None, :] if not is_batch else x

        u = np.zeros_like(x)

        for j in self.order:
            eq = self.eqs[j]
            u[:, j] = x[:, j] - (
                eq.predict(x[:, eq.parents])
                if not eq.is_root
                else np.zeros(len(x))
            )

        return u if is_batch else u[0]

    def do_sample(self, fixed, K=100, rng=None, u_noise=None):
        """
        Sample P_M(X | do(X_S=x_S)).

        The verified notebook uses a CRN tensor with shape (K, p).
        """
        S = {
            int(k): float(v)
            for k, v in fixed.items()
        }

        if u_noise is not None:
            u_noise = np.asarray(u_noise, dtype=float)
            K = u_noise.shape[0]
        elif rng is None:
            rng = np.random.default_rng(self.random_state)

        samp = np.zeros((K, self.p), dtype=float)

        for j in self.order:
            if j in S:
                samp[:, j] = S[j]
            else:
                eq = self.eqs[j]
                g = (
                    eq.predict(samp[:, eq.parents])
                    if not eq.is_root
                    else np.zeros(K, dtype=float)
                )

                if u_noise is not None:
                    noise_draw = u_noise[:, j]
                else:
                    loc, scale = self.noise[j]
                    noise_draw = rng.laplace(
                        loc=loc,
                        scale=scale,
                        size=K,
                    )

                samp[:, j] = g + noise_draw

        return samp

    def violation(self, x):
        x = np.atleast_1d(np.asarray(x, dtype=float))
        values = []

        for j in self.order:
            eq = self.eqs[j]
            loc, scale = self.noise[j]

            residual = (
                x[j] - loc
                if eq.is_root
                else x[j]
                - eq.predict(x[eq.parents])[0]
                - loc
            )

            values.append(
                abs(residual)
                / (np.sqrt(2.0) * scale + 1e-8)
            )

        return float(np.mean(values))

    def violation_details(self, x):
        x = np.atleast_1d(np.asarray(x, dtype=float))
        residuals = {}
        standardized = {}

        for j in self.order:
            eq = self.eqs[j]
            loc, scale = self.noise[j]

            if eq.is_root:
                g_value = 0.0
            else:
                g_value = eq.predict(
                    x[eq.parents].reshape(1, -1)
                )[0]

            noise_value = x[j] - g_value
            residual = noise_value - loc
            z = abs(residual) / (
                np.sqrt(2.0) * scale + 1e-8
            )

            residuals[int(j)] = float(residual)
            standardized[int(j)] = float(z)

        z_values = np.array(list(standardized.values()))
        feature_indices = list(standardized.keys())
        worst_feature = feature_indices[
            int(np.argmax(z_values))
        ]

        return {
            "residuals": residuals,
            "standardized": standardized,
            "mean": float(np.mean(z_values)),
            "median": float(np.median(z_values)),
            "p95": float(np.percentile(z_values, 95)),
            "maximum": float(np.max(z_values)),
            "worst_feature": int(worst_feature),
        }

    def noise_nll(self, x):
        x = np.asarray(x, dtype=float)
        total_nll = 0.0
        noise_values = []

        for j in self.order:
            eq = self.eqs[j]
            loc, scale = self.noise[j]

            if eq.is_root:
                g_value = 0.0
            else:
                g_value = eq.predict(
                    x[eq.parents].reshape(1, -1)
                )[0]

            u_value = x[j] - g_value

            total_nll -= sp_stats.laplace.logpdf(
                u_value,
                loc=loc,
                scale=scale,
            )

            noise_values.append(u_value)

        return {
            "nll": float(total_nll),
            "noise_values": np.asarray(noise_values),
        }


__all__ = ["ANM"]
