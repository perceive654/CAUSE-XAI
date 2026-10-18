

# # import numpy as np
# # import pandas as pd

# # from cause.diagnostics import compare_cai_shap

# # from .config import DEFAULTS
# # from .dag import discover_dag
# # from .anm import ANM
# # from .cce import counterfactual_search
# # from .cai import attribute_cai
# # from .results import UnifiedExplanation
# # from .exceptions import ANMNotFittedError
# # from .display import (
# #     show_cai_vs_shap,
# #     show_fit,
# #     show_counterfactual,
# #     show_attribution,
# #     show_explanation,
# # )
# # from sklearn.preprocessing import StandardScaler

# # class CCE_ANM_Model:
# #     """
# #     Unified CCE-ANM XAI model.

# #     This class follows the notebook implementation.

# #     API
# #     ---
# #     fit(data, f)
# #         Stage 1 + Stage 2:
# #         discover the DAG and fit the ANM.

# #     explain(x_obs, y_foil)
# #         Run both CCE and CAI and return a unified explanation.

# #     counterfactual(x_obs, y_foil)
# #         Mode A: Causal Counterfactual Explanation (CCE).

# #     attribute(x_obs)
# #         Mode B: Causal Attribution via Interventions (CAI).
# #     """

# #     def __init__(
# #         self,
# #         lambda_=None,
# #         mu=None,
# #         K_cce=None,
# #         K_cai=None,
# #         n_restarts=None,
# #         top_k=None,
# #     ):
# #         d = DEFAULTS

# #         self.lambda_ = (
# #             lambda_
# #             if lambda_ is not None
# #             else d["lambda_"]
# #         )

# #         self.mu = (
# #             mu
# #             if mu is not None
# #             else d["mu"]
# #         )

# #         self.K_cce = (
# #             K_cce
# #             if K_cce is not None
# #             else d["K_cce"]
# #         )

# #         self.K_cai = (
# #             K_cai
# #             if K_cai is not None
# #             else d["K_cai"]
# #         )

# #         self.n_restarts = (
# #             n_restarts
# #             if n_restarts is not None
# #             else d["n_restarts"]
# #         )

# #         self.top_k = (
# #             top_k
# #             if top_k is not None
# #             else d["top_k"]
# #         )

# #         # -----------------------------------------------------
# #         # Fitted attributes
# #         # -----------------------------------------------------

# #         self.anm_ = None
# #         self.sigma_ = None
# #         self.scaler_ = None

# #         self._f = None
# #         self._adj = None
# #         self._order = None

# #         # Display metadata only
# #         self.feature_names = None

# #     # =========================================================
# #     # FIT
# #     # =========================================================

# #     # def fit(
# #     #     self,
# #     #     data,
# #     #     f,
# #     #     feature_names=None,
# #     #     verbose=False,
# #     # ):
# #     #     """
# #     #     Fit the CCE-ANM model.

# #     #     This follows the notebook:

# #     #         Stage 1:
# #     #             discover DAG

# #     #         Stage 2:
# #     #             fit ANM

# #     #     Parameters
# #     #     ----------
# #     #     data : np.ndarray
# #     #         Training data of shape
# #     #         (n_samples, n_features).

# #     #     f : callable
# #     #         Black-box prediction function used by CCE/CAI.

# #     #     feature_names : list[str], optional
# #     #         Names of the input features. Used only for
# #     #         readable output.

# #     #     verbose : bool
# #     #         Whether to display fitting diagnostics.

# #     #     Returns
# #     #     -------
# #     #     CCE_ANM_Model
# #     #         Fitted model.
# #     #     """

# #     #     data = np.asarray(data, dtype=float)

# #     #     # -----------------------------------------------------
# #     #     # Store predictor
# #     #     # -----------------------------------------------------

# #     #     self._f = f

# #     #     # -----------------------------------------------------
# #     #     # Store feature names for display
# #     #     # -----------------------------------------------------

# #     #     self.feature_names = feature_names

# #     #     # =====================================================
# #     #     # Stage 1: DAG discovery
# #     #     # =====================================================

# #     #     print("[Stage 1] DAG discovery...")

# #     #     self._adj, self._order = discover_dag(
# #     #         data,
# #     #         verbose=verbose,
# #     #     )

# #     #     # =====================================================
# #     #     # Stage 2: ANM fitting
# #     #     # =====================================================

# #     #     print("\n[Stage 2] ANM fitting...")

# #     #     self.anm_ = ANM(
# #     #         self._adj,
# #     #         self._order,
# #     #         feature_names=feature_names,
# #     #     )

# #     #     self.anm_.fit(
# #     #         data,
# #     #         verbose=verbose,
# #     #     )

# #     #     # -----------------------------------------------------
# #     #     # Feature standard deviations
# #     #     # Used by CCE causal-distance calculation
# #     #     # -----------------------------------------------------

# #     #     self.sigma_ = (
# #     #         data.std(axis=0) + 1e-8
# #     #     )

# #     #     # =====================================================
# #     #     # Model ready
# #     #     # =====================================================

# #     #     show_fit(
# #     #         self,
# #     #         feature_names=self.feature_names,
# #     #         verbose=verbose,
# #     #     )

# #     #     return self


# #     def fit(self, data, f, verbose=False):
# #         if hasattr(data, "columns"):
# #             self.feature_names = list(data.columns)
# #         else:
# #             self.feature_names = None

# #         self.scaler_ = StandardScaler()
# #         data_scaled = self.scaler_.fit_transform(data)

# #         self._f = f

# #         self._adj, self._order = discover_dag(
# #             data_scaled,
# #             verbose=False
# #         )

# #         self.anm_ = ANM(
# #             self._adj,
# #             self._order
# #         )

# #         self.anm_.fit(
# #             data_scaled,
# #             verbose=False
# #         )

# #         self.sigma_ = data_scaled.std(axis=0) + 1e-8

# #         if verbose:
# #             show_fit(
# #                 self,
# #                 feature_names=self.feature_names,
# #                 verbose=verbose
# #             )

# #         return self

# #     def _check_fitted(self):
# #         """
# #         Check whether the ANM has been fitted.
# #         """

# #         if self.anm_ is None:
# #             raise ANMNotFittedError(
# #                 "This CCE_ANM_Model instance is not fitted yet. "
# #                 "Call fit(data, f) before using "
# #                 "explain/counterfactual/attribute."
# #             )

# #     def _transform_input(self, x):
# #         if isinstance(x, pd.Series):
# #             x = x.to_frame().T

# #         elif isinstance(x, np.ndarray):
# #             if x.ndim == 1:
# #                 x = x.reshape(1, -1)

# #             x = pd.DataFrame(
# #                 x,
# #                 columns=self.feature_names
# #             )

# #         return self.scaler_.transform(x)[0]

# #     # =========================================================
# #     # MODE A — CCE
# #     # =========================================================

# #     def counterfactual(
# #         self,
# #         x_obs,
# #         y_foil,
# #         non_actionable=None,
# #         verbose=False,
# #     ):
# #         """
# #         Compute a Causal Counterfactual Explanation.

# #         The actual CCE logic is implemented in
# #         counterfactual_search(), following the notebook.
# #         """
# #         x_obs = self._transform_input(x_obs)

# #         self._check_fitted()
     
# #         result = counterfactual_search(
# #             self,
# #             x_obs,
# #             y_foil,
# #             non_actionable=non_actionable,
# #             verbose=False,
# #         )

# #         if verbose:
# #             show_counterfactual(
# #                 result,
# #                 feature_names=self.feature_names,
# #             )

# #         return result

# #     # =========================================================
# #     # MODE B — CAI
# #     # =========================================================

# #     def attribute(
# #         self,
# #         x_obs,
# #         feature_names=None,
# #         verbose=False,
# #     ):
# #         """
# #         Compute Causal Attribution via Interventions.

# #         The actual CAI logic is implemented in
# #         attribute_cai(), following the notebook.
# #         """
# #         x_obs = self._transform_input(x_obs)

# #         self._check_fitted()

# #         if feature_names is None:
# #             feature_names = self.feature_names

# #         result = attribute_cai(
# #             self,
# #             x_obs,
# #             feature_names=feature_names,
# #             verbose=False,
# #         )

# #         if verbose:
# #             show_attribution(
# #                 result,
# #                 feature_names=feature_names,
# #             )

# #         return result

# #     # =========================================================
# #     # UNIFIED EXPLANATION
# #     # =========================================================

# #     def explain(
# #         self,
# #         x_obs,
# #         y_foil,
# #         feature_names=None,
# #         verbose=False,
# #     ):
# #         """
# #         Run both CCE and CAI and return a UnifiedExplanation.

# #         Execution order follows the notebook:

# #             1. CCE counterfactual
# #             2. CAI attribution
# #             3. Unified result
# #         """
# #         x_obs = self._transform_input(x_obs)

# #         self._check_fitted()

# #         if feature_names is None:
# #             feature_names = self.feature_names

# #         # -----------------------------------------------------
# #         # Mode A: CCE
# #         # -----------------------------------------------------

# #         cce_result = counterfactual_search(
# #             self,
# #             x_obs,
# #             y_foil,
# #             verbose=False,
# #         )

# #         cai_result = attribute_cai(
# #             self,
# #             x_obs,
# #             feature_names=feature_names,
# #             verbose=False,
# #         )

# #         # -----------------------------------------------------
# #         # Unified result
# #         # -----------------------------------------------------

# #         explanation = UnifiedExplanation(
# #             x_obs=np.asarray(x_obs, dtype=float),
# #             y_fact=cce_result.y_fact,
# #             y_foil=y_foil,
# #             cce=cce_result,
# #             cai=cai_result,
# #             feature_names=feature_names,
# #         )

# #         if verbose:
# #             show_explanation(
# #                 explanation,
# #                 feature_names=feature_names,
# #             )

# #         return explanation

# #     def comp_shap_cai(self, x_obs, K=200, verbose=False):
# #         x_obs = self._transform_input(x_obs)

# #         result = compare_cai_shap(
# #             self.anm_,
# #             self._f,
# #             x_obs,
# #             K=K,
# #             verbose=False
# #         )

# #         if verbose:
# #             show_cai_vs_shap(result)

# #         return result

# """
# Public CAUSE-XAI model orchestration.

# This module owns the public workflow:

#     fit()
#     counterfactual()
#     attribute()
#     explain()
#     explain_all()
#     comp_shap_cai()

# Numerical algorithms remain in their dedicated modules:
#     - dag.py
#     - anm.py
#     - cce.py
#     - cai.py
#     - diagnostics.py

# The public model methods only orchestrate those computations and,
# when requested, call the user-facing display functions.

# `explain_all()` is the single-call workflow. It computes:
#     1. CCE
#     2. CAI
#     3. CAI-vs-SHAP-style comparison

# and returns one UnifiedExplanation containing the complete
# user-facing information and JSON-ready serialization.
# """

# import numpy as np
# import pandas as pd

# from sklearn.preprocessing import StandardScaler

# from .config import DEFAULTS
# from .dag import discover_dag
# from .anm import ANM
# from .cce import counterfactual_search
# from .cai import attribute_cai
# from .diagnostics import compare_cai_shap
# from .results import UnifiedExplanation
# from .exceptions import ANMNotFittedError
# from .display import (
#     show_cai_vs_shap,
#     show_fit,
#     show_counterfactual,
#     show_attribution,
#     show_explanation,
# )


# class CCE_ANM_Model:
#     """
#     Unified CCE-ANM XAI model.

#     Public workflow
#     ---------------

#     fit(data, f)
#         Discover the causal DAG and fit the ANM.

#     counterfactual(x_obs, y_foil)
#         Compute Causal Counterfactual Explanation (CCE).

#     attribute(x_obs)
#         Compute Causal Attribution via Interventions (CAI).

#     explain(x_obs, y_foil)
#         Compute CCE + CAI and return UnifiedExplanation.

#     comp_shap_cai(x_obs)
#         Compute the CAI-vs-SHAP-style comparison.

#     explain_all(x_obs, y_foil)
#         Run the complete explanation workflow in one public call:
#         CCE + CAI + CAI-vs-SHAP-style comparison.

#     Notes
#     -----
#     The model standardizes the data internally for DAG/ANM fitting.
#     Public feature values passed to CCE/CAI are transformed internally
#     before the causal calculations, matching the current package
#     preprocessing boundary.
#     """

#     def __init__(
#         self,
#         lambda_=None,
#         mu=None,
#         K_cce=None,
#         K_cai=None,
#         n_restarts=None,
#         top_k=None,
#     ):
#         d = DEFAULTS

#         self.lambda_ = (
#             lambda_
#             if lambda_ is not None
#             else d["lambda_"]
#         )

#         self.mu = (
#             mu
#             if mu is not None
#             else d["mu"]
#         )

#         self.K_cce = (
#             K_cce
#             if K_cce is not None
#             else d["K_cce"]
#         )

#         self.K_cai = (
#             K_cai
#             if K_cai is not None
#             else d["K_cai"]
#         )

#         self.n_restarts = (
#             n_restarts
#             if n_restarts is not None
#             else d["n_restarts"]
#         )

#         self.top_k = (
#             top_k
#             if top_k is not None
#             else d["top_k"]
#         )

#         # Fitted attributes.
#         self.anm_ = None
#         self.sigma_ = None
#         self.scaler_ = None

#         self._f = None
#         self._adj = None
#         self._order = None

#         # Display/application metadata.
#         self.feature_names = None

#     # =========================================================
#     # FIT
#     # =========================================================

#     def fit(self, data, f, verbose=False):
#         """
#         Fit the causal explanation model.

#         Parameters
#         ----------
#         data : numpy.ndarray or pandas.DataFrame
#             Background/training data with shape
#             (n_samples, n_features).

#         f : callable
#             Black-box prediction function.

#         verbose : bool, default=False
#             If True, display the fitted causal structure.

#         Returns
#         -------
#         CCE_ANM_Model
#             The fitted model.
#         """
#         if hasattr(data, "columns"):
#             self.feature_names = list(data.columns)
#         else:
#             self.feature_names = None

#         self.scaler_ = StandardScaler()

#         data_scaled = self.scaler_.fit_transform(
#             data
#         )

#         self._f = f

#         self._adj, self._order = discover_dag(
#             data_scaled,
#             verbose=False,
#         )

#         self.anm_ = ANM(
#             self._adj,
#             self._order,
#         )

#         self.anm_.fit(
#             data_scaled,
#             verbose=False,
#         )

#         self.sigma_ = (
#             data_scaled.std(axis=0) + 1e-8
#         )

#         if verbose:
#             show_fit(
#                 self,
#                 feature_names=self.feature_names,
#                 verbose=verbose,
#             )

#         return self

#     # =========================================================
#     # VALIDATION / INPUT
#     # =========================================================

#     def _check_fitted(self):
#         """Raise a clear error when the model is not fitted."""
#         if self.anm_ is None:
#             raise ANMNotFittedError(
#                 "This CCE_ANM_Model instance is not fitted yet. "
#                 "Call fit(data, f) before using "
#                 "explain/counterfactual/attribute."
#             )

#     def _transform_input(self, x):
#         """
#         Transform one public observation into the internal
#         standardized one-dimensional representation.
#         """
#         self._check_fitted()

#         if isinstance(x, pd.Series):
#             x = x.to_frame().T

#         elif isinstance(x, np.ndarray):
#             if x.ndim == 1:
#                 x = x.reshape(1, -1)

#             if x.ndim != 2:
#                 raise ValueError(
#                     "x must be a one-dimensional observation "
#                     "or a two-dimensional array with one row."
#                 )

#             columns = self.feature_names

#             if columns is None:
#                 columns = list(
#                     range(x.shape[1])
#                 )

#             x = pd.DataFrame(
#                 x,
#                 columns=columns,
#             )

#         else:
#             x = np.asarray(x)

#             if x.ndim == 1:
#                 x = x.reshape(1, -1)

#             if x.ndim != 2:
#                 raise ValueError(
#                     "x must be a one-dimensional observation "
#                     "or a two-dimensional array with one row."
#                 )

#             columns = self.feature_names

#             if columns is None:
#                 columns = list(
#                     range(x.shape[1])
#                 )

#             x = pd.DataFrame(
#                 x,
#                 columns=columns,
#             )

#         if len(x) != 1:
#             raise ValueError(
#                 "Only one observation can be explained at a time."
#             )

#         transformed = self.scaler_.transform(x)

#         # CCE/CAI expect shape (p,), not (1,p).
#         return np.asarray(
#             transformed[0],
#             dtype=float,
#         )

#     def _resolve_feature_names(self, feature_names=None):
#         """Resolve explicit names against names learned during fit."""
#         if feature_names is not None:
#             names = list(feature_names)
#         else:
#             names = self.feature_names

#         if names is None:
#             return None

#         if self.anm_ is not None:
#             p = self.anm_.p

#             if len(names) != p:
#                 raise ValueError(
#                     f"feature_names must contain {p} names; "
#                     f"got {len(names)}."
#                 )

#         return names

#     # =========================================================
#     # MODE A — CCE
#     # =========================================================

#     def counterfactual(
#         self,
#         x_obs,
#         y_foil,
#         non_actionable=None,
#         verbose=False,
#     ):
#         """
#         Compute a Causal Counterfactual Explanation.

#         Parameters
#         ----------
#         x_obs : array-like
#             One observed feature vector.

#         y_foil : float
#             Desired target output/class.

#         non_actionable : list, optional
#             Feature names or indices that cannot be directly
#             intervened on.

#         verbose : bool, default=False
#             If True, display the human-readable CCE result.

#         Returns
#         -------
#         CCEResult
#         """
#         self._check_fitted()

#         x_obs = self._transform_input(x_obs)

#         result = counterfactual_search(
#             self,
#             x_obs,
#             y_foil,
#             non_actionable=non_actionable,
#             verbose=False,
#         )

#         if verbose:
#             show_counterfactual(
#                 result,
#                 feature_names=self.feature_names,
#             )

#         return result

#     # =========================================================
#     # MODE B — CAI
#     # =========================================================

#     def attribute(
#         self,
#         x_obs,
#         feature_names=None,
#         verbose=False,
#     ):
#         """
#         Compute Causal Attribution via Interventions.

#         Parameters
#         ----------
#         x_obs : array-like
#             One observed feature vector.

#         feature_names : list[str], optional
#             Names used in the result/display.

#         verbose : bool, default=False
#             If True, display the human-readable CAI result.

#         Returns
#         -------
#         CAIResult
#         """
#         self._check_fitted()

#         x_obs = self._transform_input(x_obs)

#         feature_names = self._resolve_feature_names(
#             feature_names
#         )

#         result = attribute_cai(
#             self,
#             x_obs,
#             feature_names=feature_names,
#             verbose=False,
#         )

#         if verbose:
#             show_attribution(
#                 result,
#                 feature_names=feature_names,
#             )

#         return result

#     # =========================================================
#     # UNIFIED CCE + CAI
#     # =========================================================

#     def explain(
#         self,
#         x_obs,
#         y_foil,
#         feature_names=None,
#         non_actionable=None,
#         verbose=False,
#     ):
#         """
#         Run CCE + CAI and return one UnifiedExplanation.

#         This method intentionally does not call the public
#         counterfactual() and attribute() methods because those
#         methods can display results. The raw computational functions
#         are called directly so the unified workflow performs each
#         computation exactly once.
#         """
#         self._check_fitted()

#         x_obs = self._transform_input(x_obs)

#         feature_names = self._resolve_feature_names(
#             feature_names
#         )

#         # -----------------------------------------------------
#         # Mode A: CCE
#         # -----------------------------------------------------

#         cce_result = counterfactual_search(
#             self,
#             x_obs,
#             y_foil,
#             non_actionable=non_actionable,
#             verbose=False,
#         )

#         # -----------------------------------------------------
#         # Mode B: CAI
#         # -----------------------------------------------------

#         cai_result = attribute_cai(
#             self,
#             x_obs,
#             feature_names=feature_names,
#             verbose=False,
#         )

#         explanation = UnifiedExplanation(
#             x_obs=np.asarray(
#                 x_obs,
#                 dtype=float,
#             ),
#             y_fact=float(
#                 cce_result.y_fact
#             ),
#             y_foil=float(y_foil),
#             cce=cce_result,
#             cai=cai_result,
#             feature_names=feature_names,
#         )

#         if verbose:
#             show_explanation(
#                 explanation,
#                 feature_names=feature_names,
#             )

#         return explanation

#     # =========================================================
#     # CAI VS SHAP-STYLE COMPARISON
#     # =========================================================

#     def comp_shap_cai(
#         self,
#         x_obs,
#         K=200,
#         verbose=False,
#     ):
#         """
#         Compare interventional CAI against the observational
#         SHAP-style attribution.

#         Parameters
#         ----------
#         x_obs : array-like
#             One observed feature vector.

#         K : int, default=200
#             Number of Monte Carlo samples.

#         verbose : bool, default=False
#             If True, display the comparison.

#         Returns
#         -------
#         dict
#             Diagnostic comparison output.
#         """
#         self._check_fitted()

#         x_obs = self._transform_input(x_obs)

#         result = compare_cai_shap(
#             self.anm_,
#             self._f,
#             x_obs,
#             K=K,
#             verbose=False,
#         )

#         if verbose:
#             show_cai_vs_shap(result)

#         return result

#     # =========================================================
#     # COMPLETE ONE-CALL WORKFLOW
#     # =========================================================

#     def explain_all(
#         self,
#         x_obs,
#         y_foil,
#         feature_names=None,
#         non_actionable=None,
#         K=None,
#         verbose=False,
#     ):
#         """
#         Run the complete CAUSE-XAI explanation workflow in one call.

#         The workflow is:

#             1. Causal Counterfactual Explanation (CCE)
#             2. Causal Attribution via Interventions (CAI)
#             3. CAI-vs-SHAP-style comparison

#         The three computations are performed once and combined into
#         one UnifiedExplanation.

#         Parameters
#         ----------
#         x_obs : array-like
#             One observed feature vector.

#         y_foil : float
#             Desired target output/class for CCE.

#         feature_names : list[str], optional
#             Feature names for the result.

#         non_actionable : list, optional
#             Feature names or indices that cannot be directly
#             intervened on by CCE. These features are still included
#             in CAI because CAI estimates the causal effect of every
#             feature.

#         K : int, optional
#             Monte Carlo sample count for the CAI-vs-SHAP-style
#             comparison. If omitted, the model's K_cai setting is used.

#         verbose : bool, default=False
#             If True, display the complete unified explanation and
#             the CAI-vs-SHAP comparison.

#         Returns
#         -------
#         UnifiedExplanation
#             A single structured result containing:

#                 result.cce
#                 result.cai
#                 result.comparison

#             Use:

#                 result.to_dict()

#             for complete JSON-ready Python data, or:

#                 result.to_json()

#             for a JSON string.

#         Notes
#         -----
#         This method does not call the public methods
#         counterfactual(), attribute(), explain(), or
#         comp_shap_cai(). It calls the raw computation functions
#         directly to avoid duplicated work and duplicated displays.
#         """
#         self._check_fitted()

#         x_obs = self._transform_input(x_obs)

#         feature_names = self._resolve_feature_names(
#             feature_names
#         )

#         # -----------------------------------------------------
#         # 1. CCE
#         # -----------------------------------------------------

#         cce_result = counterfactual_search(
#             self,
#             x_obs,
#             y_foil,
#             non_actionable=non_actionable,
#             verbose=False,
#         )

#         # -----------------------------------------------------
#         # 2. CAI
#         # -----------------------------------------------------

#         cai_result = attribute_cai(
#             self,
#             x_obs,
#             feature_names=feature_names,
#             verbose=False,
#         )

#         # -----------------------------------------------------
#         # 3. CAI vs SHAP-style
#         # -----------------------------------------------------

#         comparison_K = (
#             self.K_cai
#             if K is None
#             else K
#         )

#         comparison = compare_cai_shap(
#             self.anm_,
#             self._f,
#             x_obs,
#             K=comparison_K,
#             verbose=False,
#         )

#         # -----------------------------------------------------
#         # Unified structured result
#         # -----------------------------------------------------

#         explanation = UnifiedExplanation(
#             x_obs=np.asarray(
#                 x_obs,
#                 dtype=float,
#             ),
#             y_fact=float(
#                 cce_result.y_fact
#             ),
#             y_foil=float(y_foil),
#             cce=cce_result,
#             cai=cai_result,
#             feature_names=feature_names,
#             comparison=comparison,
#         )

#         # -----------------------------------------------------
#         # User-facing display
#         # -----------------------------------------------------

#         if verbose:
#             show_explanation(
#                 explanation,
#                 feature_names=feature_names,
#             )

#             show_cai_vs_shap(
#                 comparison
#             )

#         return explanation


# __all__ = [
#     "CCE_ANM_Model",
# ]


"""Public CCE-ANM model interface."""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from .anm import ANM
from .cai import attribute_cai
from .cce import counterfactual_search
from .config import DEFAULTS
from .dag import discover_dag
from .diagnostics import compare_cai_shap
from .display import (
    show_attribution,
    show_cai_vs_shap,
    show_counterfactual,
    show_explanation,
    show_fit,
)
from .results import UnifiedExplanation


class CCE_ANM_Model:
    """
    Unified CCE-ANM XAI Model.

    Constructor parameters intentionally match the verified notebook.
    Raw user data is accepted by fit(); StandardScaler is applied
    internally before DAG discovery and ANM fitting.
    """

    def __init__(
        self,
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
    ):
        self.lambda_ = lambda_
        self.mu = mu
        self.K_cce = int(K_cce)
        self.K_cai = int(K_cai)
        self.top_k = int(top_k)
        self.target_prob = float(target_prob)
        self.search_feasibility = (
            search_feasibility
        )
        self.random_state = int(
            random_state
        )
        self.percentile = float(
            percentile
        )
        self.cycle_strategy = (
            cycle_strategy
        )

        self.anm_ = None
        self.sigma_ = None
        self.scaler_ = None

        self._f = None
        self._adj = None
        self._order = None

        self.feature_names = None
        self.n_features_in_ = None
        self.is_fitted_ = False

    def fit(
        self,
        data,
        f,
        verbose=True,
    ):
        """
        Fit the model.

        `data` is raw user-space data. It is standardized internally.
        The supplied black-box prediction function is expected to
        operate on that same standardized representation.
        """
        if hasattr(data, "columns"):
            self.feature_names = list(
                data.columns
            )
            X = data.to_numpy(
                dtype=float
            )
        else:
            self.feature_names = None
            X = np.asarray(
                data,
                dtype=float,
            )

        if X.ndim != 2:
            raise ValueError(
                "data must be a 2D feature matrix"
            )

        if not np.all(np.isfinite(X)):
            raise ValueError(
                "data contains NaN or infinite values"
            )

        self.n_features_in_ = X.shape[1]

        if self.feature_names is None:
            self.feature_names = [
                f"X{i + 1}"
                for i in range(
                    self.n_features_in_
                )
            ]

        if len(self.feature_names) != (
            self.n_features_in_
        ):
            raise ValueError(
                "feature_names length must match "
                "the number of input features"
            )

        self.scaler_ = StandardScaler().fit(X)
        X_model = self.scaler_.transform(X)

        self._f = f

        self._adj, self._order = discover_dag(
            X_model,
            verbose=False,
            random_state=self.random_state,
            cycle_strategy=self.cycle_strategy,
            percentile=self.percentile,
        )

        self.anm_ = ANM(
            self._adj,
            self._order,
            random_state=self.random_state,
        )

        self.anm_.fit(
            X_model,
            verbose=False,
        )

        self.sigma_ = (
            X_model.std(axis=0)
            + 1e-8
        )

        self.is_fitted_ = True

        if verbose:
            show_fit(
                self,
                feature_names=self.feature_names,
                verbose=verbose,
            )

        return self

    def _check_fitted(self):
        if (
            not self.is_fitted_
            or self.anm_ is None
            or self.scaler_ is None
            or self._f is None
        ):
            raise RuntimeError(
                "CCE_ANM_Model must be fitted before "
                "calling this method."
            )

    def _transform_input(self, x):
        self._check_fitted()

        if isinstance(x, pd.Series):
            x = x.to_numpy(
                dtype=float
            )
        elif hasattr(x, "to_numpy"):
            x = x.to_numpy(
                dtype=float
            )

        x = np.asarray(
            x,
            dtype=float,
        )

        if x.ndim == 1:
            x = x.reshape(1, -1)

        if x.ndim != 2:
            raise ValueError(
                "x_obs must be a 1D vector or "
                "a single-row 2D array"
            )

        if x.shape[0] != 1:
            raise ValueError(
                "x_obs must contain exactly one observation"
            )

        if x.shape[1] != self.n_features_in_:
            raise ValueError(
                f"x_obs must contain "
                f"{self.n_features_in_} features"
            )

        if not np.all(np.isfinite(x)):
            raise ValueError(
                "x_obs contains NaN or infinite values"
            )

        return self.scaler_.transform(x)[0]

    def counterfactual(
        self,
        x_obs,
        y_foil=1.0,
        non_actionable=None,
        verbose=False,
    ):
        x_obs_scaled = self._transform_input(
            x_obs
        )

        result = counterfactual_search(
            self,
            x_obs_scaled,
            y_foil=y_foil,
            non_actionable=non_actionable,
            verbose=False,
        )

        if verbose:
            show_counterfactual(
                result,
                feature_names=self.feature_names,
            )

        return result

    def attribute(
        self,
        x_obs,
        feature_names=None,
        verbose=False,
    ):
        x_obs_scaled = self._transform_input(
            x_obs
        )

        names = (
            self.feature_names
            if feature_names is None
            else feature_names
        )

        result = attribute_cai(
            self,
            x_obs_scaled,
            feature_names=names,
            verbose=False,
        )

        if verbose:
            show_attribution(
                result,
                feature_names=names,
            )

        return result

    def explain(
        self,
        x_obs,
        y_foil,
        feature_names=None,
        non_actionable=None,
        verbose=True,
    ):
        x_obs_scaled = self._transform_input(
            x_obs
        )

        names = (
            self.feature_names
            if feature_names is None
            else feature_names
        )

        cce_result = counterfactual_search(
            self,
            x_obs_scaled,
            y_foil,
            non_actionable=non_actionable,
            verbose=False,
        )

        cai_result = attribute_cai(
            self,
            x_obs_scaled,
            feature_names=names,
            verbose=False,
        )

        explanation = UnifiedExplanation(
            x_obs=np.asarray(
                x_obs_scaled,
                dtype=float,
            ),
            y_fact=float(
                cce_result.y_fact
            ),
            y_foil=float(y_foil),
            cce=cce_result,
            cai=cai_result,
            feature_names=names,
        )

        if verbose:
            show_explanation(
                explanation,
                feature_names=names,
            )

        return explanation

    def comp_shap_cai(
        self,
        x_obs,
        K=200,
        verbose=False,
    ):
        x_obs_scaled = self._transform_input(
            x_obs
        )

        comparison = compare_cai_shap(
            self.anm_,
            self._f,
            x_obs_scaled,
            K=K,
            verbose=False,
        )

        if verbose:
            show_cai_vs_shap(
                comparison,
                feature_names=self.feature_names,
            )

        return comparison

    def explain_all(
        self,
        x_obs,
        y_foil,
        feature_names=None,
        K=None,
        verbose=True,
    ):
        """
        One-call orchestration only.

        The numerical algorithms remain the verified notebook
        implementations. This method only wires CCE, CAI and the
        CAI-vs-SHAP diagnostic together.
        """
        x_obs_scaled = self._transform_input(
            x_obs
        )

        names = (
            self.feature_names
            if feature_names is None
            else feature_names
        )

        cce_result = counterfactual_search(
            self,
            x_obs_scaled,
            y_foil,
            non_actionable=non_actionable,
            verbose=False,
        )

        cai_result = attribute_cai(
            self,
            x_obs_scaled,
            feature_names=names,
            verbose=False,
        )

        comparison = compare_cai_shap(
            self.anm_,
            self._f,
            x_obs_scaled,
            K=(
                self.K_cai
                if K is None
                else K
            ),
            verbose=False,
        )

        explanation = UnifiedExplanation(
            x_obs=np.asarray(
                x_obs_scaled,
                dtype=float,
            ),
            y_fact=float(
                cce_result.y_fact
            ),
            y_foil=float(y_foil),
            cce=cce_result,
            cai=cai_result,
            feature_names=names,
            comparison=comparison,
        )

        if verbose:
            show_explanation(
                explanation,
                feature_names=names,
            )
            show_cai_vs_shap(
                comparison,
                feature_names=names,
            )

        return explanation


__all__ = [
    "CCE_ANM_Model",
]
