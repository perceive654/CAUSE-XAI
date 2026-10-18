

# # # # """
# # # # Result dataclasses for CAUSE-XAI.

# # # # These classes store the numerical outputs produced by:
# # # #     - CCE: Causal Contrastive Explanation
# # # #     - CAI: Causal Attribution Index
# # # #     - UnifiedExplanation: CCE + CAI

# # # # They do not perform CCE/CAI calculations.
# # # # The display layer (cause.display) is responsible for
# # # # human-readable output.
# # # # """

# # # # from dataclasses import dataclass
# # # # from typing import Optional, List

# # # # import numpy as np


# # # # # ============================================================
# # # # # CCE RESULT
# # # # # ============================================================

# # # # @dataclass
# # # # class CCEResult:
# # # #     """
# # # #     Mode A: Causal Contrastive Explanation result.

# # # #     Stores the factual observation, counterfactual observation,
# # # #     latent representations, prediction values, causal validity
# # # #     metrics, and intervention information.
# # # #     """

# # # #     # --------------------------------------------------------
# # # #     # Observed and counterfactual states
# # # #     # --------------------------------------------------------
# # # #     x_obs: np.ndarray
# # # #     x_star: np.ndarray

# # # #     # --------------------------------------------------------
# # # #     # ANM latent/noise representations
# # # #     # --------------------------------------------------------
# # # #     u_obs: np.ndarray
# # # #     u_star: np.ndarray

# # # #     # --------------------------------------------------------
# # # #     # Prediction information
# # # #     # --------------------------------------------------------
# # # #     y_fact: float
# # # #     y_foil: float
# # # #     y_achieved: float

# # # #     # --------------------------------------------------------
# # # #     # Causal validity / optimization metrics
# # # #     # --------------------------------------------------------
# # # #     violation: float
# # # #     d_causal: float
# # # #     sparsity: float

# # # #     # --------------------------------------------------------
# # # #     # Changed observed features
# # # #     # --------------------------------------------------------
# # # #     changed: List[int]

# # # #     # --------------------------------------------------------
# # # #     # Runtime and feasibility
# # # #     # --------------------------------------------------------
# # # #     runtime: float
# # # #     feasible: bool

# # # #     # --------------------------------------------------------
# # # #     # Features directly intervened on
# # # #     # --------------------------------------------------------
# # # #     direct_interventions: Optional[List[int]] = None

# # # #     def summary(
# # # #         self,
# # # #         feature_names=None,
    
# # # #     ):
# # # #         """
# # # #         Display the CCE counterfactual result.

# # # #         No calculation is performed here.
# # # #         """

# # # #         from .display import show_counterfactual

# # # #         names = feature_names

# # # #         show_counterfactual(
# # # #             self,
# # # #             feature_names=names,
          
# # # #         )


# # # # # ============================================================
# # # # # CAI RESULT
# # # # # ============================================================

# # # # @dataclass
# # # # class CAIResult:
# # # #     """
# # # #     Mode B: Causal Attribution Index result.

# # # #     Stores the CAI values and the Monte Carlo quantities
# # # #     produced during CAI computation.
# # # #     """

# # # #     # --------------------------------------------------------
# # # #     # Observation and CAI values
# # # #     # --------------------------------------------------------
# # # #     x_obs: np.ndarray
# # # #     cai: np.ndarray
# # # #     cai_norm: np.ndarray

# # # #     # --------------------------------------------------------
# # # #     # Baseline and intervention expectations
# # # #     # --------------------------------------------------------
# # # #     baseline: float
# # # #     f_do: np.ndarray

# # # #     # --------------------------------------------------------
# # # #     # Feature names
# # # #     # --------------------------------------------------------
# # # #     feature_names: Optional[List[str]] = None

# # # #     # --------------------------------------------------------
# # # #     # Monte Carlo uncertainty diagnostics
# # # #     # --------------------------------------------------------
# # # #     standard_errors: Optional[np.ndarray] = None
# # # #     confidence_intervals: Optional[np.ndarray] = None
# # # #     intervention_values: Optional[list] = None
# # # #     n_samples: Optional[int] = None

# # # #     def summary(
# # # #         self,
# # # #         feature_names=None,

# # # #     ):
# # # #         """
# # # #         Display the CAI attribution result.

# # # #         No calculation is performed here.
# # # #         """

# # # #         from .display import show_attribution

# # # #         names = feature_names or self.feature_names

# # # #         show_attribution(
# # # #             self,
# # # #             feature_names=names,
# # # #         )


# # # # # ============================================================
# # # # # UNIFIED EXPLANATION
# # # # # ============================================================

# # # # @dataclass
# # # # class UnifiedExplanation:
# # # #     """
# # # #     Full CCE-ANM explanation for one observation.

# # # #     Combines:
# # # #         - CCE counterfactual explanation
# # # #         - CAI causal attribution
# # # #     """

# # # #     # --------------------------------------------------------
# # # #     # Observation and prediction information
# # # #     # --------------------------------------------------------
# # # #     x_obs: np.ndarray
# # # #     y_fact: float
# # # #     y_foil: float

# # # #     # --------------------------------------------------------
# # # #     # CCE and CAI results
# # # #     # --------------------------------------------------------
# # # #     cce: CCEResult
# # # #     cai: CAIResult

# # # #     # --------------------------------------------------------
# # # #     # Feature names
# # # #     # --------------------------------------------------------
# # # #     feature_names: Optional[List[str]] = None

# # # #     def summary(
# # # #         self,
# # # #         feature_names=None,
# # # #         task="regression",
# # # #     ):
# # # #         """
# # # #         Display the unified CCE-ANM explanation.

# # # #         The unified display is handled by cause.display so that
# # # #         CCE and CAI information is not duplicated.
# # # #         """

# # # #         from .display import show_explanation

# # # #         names = feature_names or self.feature_names

# # # #         show_explanation(
# # # #             self,
# # # #             feature_names=names,
# # # #         )


# # # # # ============================================================
# # # # # PUBLIC API
# # # # # ============================================================

# # # # __all__ = [
# # # #     "CCEResult",
# # # #     "CAIResult",
# # # #     "UnifiedExplanation",
# # # # ]

# # # from dataclasses import dataclass
# # # from typing import Optional, List

# # # import numpy as np


# # # @dataclass
# # # class CCEResult:
# # #     x_obs: np.ndarray
# # #     x_star: np.ndarray

# # #     u_obs: np.ndarray
# # #     u_star: np.ndarray

# # #     y_fact: float
# # #     y_foil: float
# # #     y_achieved: float

# # #     violation: float
# # #     d_causal: float
# # #     sparsity: float

# # #     changed: List[int]

# # #     runtime: float
# # #     feasible: bool

# # #     direct_interventions: Optional[List[int]] = None

# # #     def summary(self, feature_names=None):
# # #         from .display import show_counterfactual

# # #         show_counterfactual(
# # #             self,
# # #             feature_names=feature_names,
# # #         )

# # #     def to_dict(self, feature_names=None):
# # #         names = feature_names

# # #         if names is None:
# # #             names = [
# # #                 f"Feature {i + 1}"
# # #                 for i in range(len(self.x_obs))
# # #             ]

# # #         changes = []

# # #         indices = self.direct_interventions or self.changed

# # #         for j in indices:
# # #             changes.append({
# # #                 "feature": names[j],
# # #                 "current_value": float(self.x_obs[j]),
# # #                 "new_value": float(self.x_star[j]),
# # #                 "change": float(self.x_star[j] - self.x_obs[j]),
# # #             })

# # #         return {
# # #             "type": "counterfactual",
# # #             "feasible": bool(self.feasible),
# # #             "current_output": float(self.y_fact),
# # #             "target_output": float(self.y_foil),
# # #             "achieved_output": float(self.y_achieved),
# # #             "changes": changes,
# # #             "causal_validity": {
# # #                 "consistent": bool(self.violation < 1.5),
# # #                 "causal_distance": float(self.d_causal),
# # #                 "causal_sparsity": float(self.sparsity),
# # #             },
# # #         }


# # # @dataclass
# # # class CAIResult:
# # #     x_obs: np.ndarray
# # #     cai: np.ndarray
# # #     cai_norm: np.ndarray

# # #     baseline: float
# # #     f_do: np.ndarray

# # #     feature_names: Optional[List[str]] = None

# # #     standard_errors: Optional[np.ndarray] = None
# # #     confidence_intervals: Optional[np.ndarray] = None
# # #     intervention_values: Optional[list] = None
# # #     n_samples: Optional[int] = None

# # #     def summary(self, feature_names=None):
# # #         from .display import show_attribution

# # #         names = feature_names or self.feature_names

# # #         show_attribution(
# # #             self,
# # #             feature_names=names,
# # #         )

# # #     def to_dict(self, feature_names=None):
# # #         names = feature_names or self.feature_names

# # #         if names is None:
# # #             names = [
# # #                 f"Feature {i + 1}"
# # #                 for i in range(len(self.cai))
# # #             ]

# # #         effects = []

# # #         for i, effect in enumerate(self.cai):
# # #             effects.append({
# # #                 "feature": names[i],
# # #                 "causal_effect": float(effect),
# # #             })

# # #         order = np.argsort(np.abs(self.cai))[::-1]

# # #         top_feature = int(order[0]) if len(order) else None

# # #         return {
# # #             "type": "causal_attribution",
# # #             "baseline_output": float(self.baseline),
# # #             "features": effects,
# # #             "top_causal_feature": (
# # #                 names[top_feature]
# # #                 if top_feature is not None
# # #                 else None
# # #             ),
# # #             "top_causal_effect": (
# # #                 float(self.cai[top_feature])
# # #                 if top_feature is not None
# # #                 else None
# # #             ),
# # #         }


# # # @dataclass
# # # class UnifiedExplanation:
# # #     x_obs: np.ndarray
# # #     y_fact: float
# # #     y_foil: float

# # #     cce: CCEResult
# # #     cai: CAIResult

# # #     feature_names: Optional[List[str]] = None

# # #     def summary(self, feature_names=None):
# # #         from .display import show_explanation

# # #         names = feature_names or self.feature_names

# # #         show_explanation(
# # #             self,
# # #             feature_names=names,
# # #         )

# # #     def to_dict(self, feature_names=None):
# # #         names = feature_names or self.feature_names

# # #         cai_dict = self.cai.to_dict(names)
# # #         cce_dict = self.cce.to_dict(names)

# # #         return {
# # #             "type": "unified_explanation",
# # #             "prediction": {
# # #                 "current_output": float(self.y_fact),
# # #                 "target_output": float(self.y_foil),
# # #                 "achieved_output": float(self.cce.y_achieved),
# # #             },
# # #             "causal_factors": cai_dict["features"][:3],
# # #             "counterfactual": {
# # #                 "feasible": cce_dict["feasible"],
# # #                 "changes": cce_dict["changes"],
# # #                 "causal_validity": cce_dict["causal_validity"],
# # #             },
# # #             "summary": {
# # #                 "top_causal_feature": cai_dict["top_causal_feature"],
# # #                 "top_causal_effect": cai_dict["top_causal_effect"],
# # #             },
# # #         }


# # # __all__ = [
# # #     "CCEResult",
# # #     "CAIResult",
# # #     "UnifiedExplanation",
# # # ]

# # """
# # Result dataclasses for CAUSE-XAI.

# # These classes store the numerical outputs produced by:

# #     - CCE: Causal Contrastive Explanation
# #     - CAI: Causal Attribution Index
# #     - UnifiedExplanation: CCE + CAI

# # They do not perform CCE/CAI calculations.

# # The display layer (cause.display) is responsible for
# # human-readable output.
# # """

# # from dataclasses import dataclass
# # from typing import Optional, List

# # import numpy as np


# # # ============================================================
# # # CCE RESULT
# # # ============================================================

# # @dataclass
# # class CCEResult:
# #     """
# #     Causal Contrastive Explanation result.

# #     Stores the factual observation, counterfactual observation,
# #     latent representations, prediction values, causal validity
# #     metrics, intervention information, and notebook-level
# #     feasibility/search diagnostics.

# #     The additional search fields correspond to the verified
# #     CCE notebook implementation.
# #     """

# #     # --------------------------------------------------------
# #     # Observed and counterfactual states
# #     # --------------------------------------------------------

# #     x_obs: np.ndarray
# #     x_star: np.ndarray

# #     # --------------------------------------------------------
# #     # ANM latent/noise representations
# #     # --------------------------------------------------------

# #     u_obs: np.ndarray
# #     u_star: np.ndarray

# #     # --------------------------------------------------------
# #     # Prediction information
# #     # --------------------------------------------------------

# #     y_fact: float
# #     y_foil: float
# #     y_achieved: float

# #     # --------------------------------------------------------
# #     # Causal validity / optimization metrics
# #     # --------------------------------------------------------

# #     violation: float
# #     d_causal: float
# #     sparsity: float

# #     # --------------------------------------------------------
# #     # Changed observed features
# #     # --------------------------------------------------------

# #     changed: List[int]

# #     # --------------------------------------------------------
# #     # Runtime and feasibility
# #     # --------------------------------------------------------

# #     runtime: float
# #     feasible: bool

# #     # --------------------------------------------------------
# #     # Features directly intervened on
# #     # --------------------------------------------------------

# #     direct_interventions: Optional[List[int]] = None

# #     # --------------------------------------------------------
# #     # Verified notebook CCE search diagnostics
# #     # --------------------------------------------------------

# #     # Whether the selected counterfactual search was feasible.
# #     search_feasible: Optional[bool] = None

# #     # Whether the requested target probability was reached.
# #     target_reached: Optional[bool] = None

# #     # Whether the search crossed the target boundary.
# #     boundary_crossed: Optional[bool] = None

# #     # Population/interventional prediction at the selected state.
# #     y_interventional: Optional[float] = None

# #     # Baseline population/interventional expectation.
# #     y_baseline_expectation: Optional[float] = None

# #     # Target probability used by the CCE oracle.
# #     target_prob: Optional[float] = None

# #     # Oracle/search feasibility description.
# #     search_feasibility: Optional[str] = None

# #     # --------------------------------------------------------
# #     # Display
# #     # --------------------------------------------------------

# #     def summary(self, feature_names=None):
# #         """
# #         Display the CCE counterfactual result.

# #         No calculation is performed here.
# #         """

# #         from .display import show_counterfactual

# #         show_counterfactual(
# #             self,
# #             feature_names=feature_names,
# #         )

# #     # --------------------------------------------------------
# #     # User-facing serialization
# #     # --------------------------------------------------------

# #     def to_dict(self, feature_names=None):
# #         """
# #         Convert the CCE result into a JSON-ready,
# #         user-facing dictionary.

# #         Internal latent ANM representations are intentionally
# #         not exposed.
# #         """

# #         names = feature_names

# #         if names is None:
# #             names = [
# #                 f"Feature {i + 1}"
# #                 for i in range(len(self.x_obs))
# #             ]

# #         changes = []

# #         indices = (
# #             self.direct_interventions
# #             if self.direct_interventions is not None
# #             else self.changed
# #         )

# #         for j in indices:
# #             changes.append({
# #                 "feature": names[j],
# #                 "current_value": float(self.x_obs[j]),
# #                 "new_value": float(self.x_star[j]),
# #                 "change": float(
# #                     self.x_star[j] - self.x_obs[j]
# #                 ),
# #             })

# #         causal_validity = {
# #             "consistent": bool(self.violation < 1.5),
# #             "causal_distance": float(self.d_causal),
# #             "causal_sparsity": float(self.sparsity),
# #         }

# #         result = {
# #             "type": "counterfactual",
# #             "feasible": bool(self.feasible),
# #             "current_output": float(self.y_fact),
# #             "target_output": float(self.y_foil),
# #             "achieved_output": float(self.y_achieved),
# #             "changes": changes,
# #             "causal_validity": causal_validity,
# #         }

# #         # ----------------------------------------------------
# #         # Verified notebook diagnostics
# #         # ----------------------------------------------------

# #         if self.search_feasible is not None:
# #             result["search_feasible"] = bool(
# #                 self.search_feasible
# #             )

# #         if self.target_reached is not None:
# #             result["target_reached"] = bool(
# #                 self.target_reached
# #             )

# #         if self.boundary_crossed is not None:
# #             result["boundary_crossed"] = bool(
# #                 self.boundary_crossed
# #             )

# #         if self.y_interventional is not None:
# #             result["y_interventional"] = float(
# #                 self.y_interventional
# #             )

# #         if self.y_baseline_expectation is not None:
# #             result["y_baseline_expectation"] = float(
# #                 self.y_baseline_expectation
# #             )

# #         if self.target_prob is not None:
# #             result["target_probability"] = float(
# #                 self.target_prob
# #             )

# #         if self.search_feasibility is not None:
# #             result["search_feasibility"] = (
# #                 self.search_feasibility
# #             )

# #         return result


# # # ============================================================
# # # CAI RESULT
# # # ============================================================

# # @dataclass
# # class CAIResult:
# #     """
# #     Causal Attribution Index result.

# #     Stores the CAI values and Monte Carlo quantities produced
# #     during CAI computation.

# #     The uncertainty fields include the paired CRN-based
# #     estimates from the verified notebook and the corresponding
# #     unpaired diagnostics.
# #     """

# #     # --------------------------------------------------------
# #     # Observation and CAI values
# #     # --------------------------------------------------------

# #     x_obs: np.ndarray

# #     cai: np.ndarray
# #     cai_norm: np.ndarray

# #     # --------------------------------------------------------
# #     # Baseline and intervention expectations
# #     # --------------------------------------------------------

# #     baseline: float
# #     f_do: np.ndarray

# #     # --------------------------------------------------------
# #     # Feature names
# #     # --------------------------------------------------------

# #     feature_names: Optional[List[str]] = None

# #     # --------------------------------------------------------
# #     # Paired Monte Carlo uncertainty
# #     # --------------------------------------------------------

# #     standard_errors: Optional[np.ndarray] = None
# #     confidence_intervals: Optional[np.ndarray] = None

# #     # --------------------------------------------------------
# #     # Intervention values / sample count
# #     # --------------------------------------------------------

# #     intervention_values: Optional[list] = None
# #     n_samples: Optional[int] = None

# #     # --------------------------------------------------------
# #     # Verified notebook unpaired diagnostics
# #     # --------------------------------------------------------

# #     # SE obtained without pairing the baseline/intervention
# #     # Monte Carlo samples.
# #     unpaired_standard_errors: Optional[np.ndarray] = None

# #     # Variance reduction obtained from common random numbers.
# #     variance_reduction: Optional[np.ndarray] = None

# #     # --------------------------------------------------------
# #     # Display
# #     # --------------------------------------------------------

# #     def summary(self, feature_names=None):
# #         """
# #         Display the CAI attribution result.

# #         No calculation is performed here.
# #         """

# #         from .display import show_attribution

# #         names = feature_names or self.feature_names

# #         show_attribution(
# #             self,
# #             feature_names=names,
# #         )

# #     # --------------------------------------------------------
# #     # User-facing serialization
# #     # --------------------------------------------------------

# #     def to_dict(self, feature_names=None):
# #         """
# #         Convert the CAI result into a JSON-ready,
# #         user-facing dictionary.
# #         """

# #         names = feature_names or self.feature_names

# #         if names is None:
# #             names = [
# #                 f"Feature {i + 1}"
# #                 for i in range(len(self.cai))
# #             ]

# #         effects = []

# #         for i, effect in enumerate(self.cai):
# #             item = {
# #                 "feature": names[i],
# #                 "causal_effect": float(effect),
# #             }

# #             if (
# #                 self.intervention_values is not None
# #                 and i < len(self.intervention_values)
# #             ):
# #                 item["intervention"] = float(
# #                     self.intervention_values[i]
# #                 )

# #             if (
# #                 self.standard_errors is not None
# #                 and i < len(self.standard_errors)
# #             ):
# #                 item["standard_error"] = float(
# #                     self.standard_errors[i]
# #                 )

# #             if (
# #                 self.confidence_intervals is not None
# #                 and i < len(self.confidence_intervals)
# #             ):
# #                 ci = self.confidence_intervals[i]

# #                 item["confidence_interval_95"] = [
# #                     float(ci[0]),
# #                     float(ci[1]),
# #                 ]

# #             effects.append(item)

# #         order = np.argsort(np.abs(self.cai))[::-1]

# #         top_feature = (
# #             int(order[0])
# #             if len(order)
# #             else None
# #         )

# #         result = {
# #             "type": "causal_attribution",

# #             "baseline_output": float(
# #                 self.baseline
# #             ),

# #             "features": effects,

# #             "top_causal_feature": (
# #                 names[top_feature]
# #                 if top_feature is not None
# #                 else None
# #             ),

# #             "top_causal_effect": (
# #                 float(self.cai[top_feature])
# #                 if top_feature is not None
# #                 else None
# #             ),
# #         }

# #         # ----------------------------------------------------
# #         # Monte Carlo metadata
# #         # ----------------------------------------------------

# #         if self.n_samples is not None:
# #             result["n_samples"] = int(
# #                 self.n_samples
# #             )

# #         return result


# # # ============================================================
# # # UNIFIED EXPLANATION
# # # ============================================================

# # @dataclass
# # class UnifiedExplanation:
# #     """
# #     Full CCE-ANM explanation for one observation.

# #     Combines:

# #         - CCE counterfactual explanation
# #         - CAI causal attribution
# #     """

# #     # --------------------------------------------------------
# #     # Observation and prediction information
# #     # --------------------------------------------------------

# #     x_obs: np.ndarray

# #     y_fact: float
# #     y_foil: float

# #     # --------------------------------------------------------
# #     # CCE and CAI results
# #     # --------------------------------------------------------

# #     cce: CCEResult
# #     cai: CAIResult

# #     # --------------------------------------------------------
# #     # Feature names
# #     # --------------------------------------------------------

# #     feature_names: Optional[List[str]] = None

# #     # --------------------------------------------------------
# #     # Display
# #     # --------------------------------------------------------

# #     def summary(self, feature_names=None):
# #         """
# #         Display the unified CCE-ANM explanation.

# #         The unified display is handled by cause.display so that
# #         CCE and CAI information is not duplicated.
# #         """

# #         from .display import show_explanation

# #         names = feature_names or self.feature_names

# #         show_explanation(
# #             self,
# #             feature_names=names,
# #         )

# #     # --------------------------------------------------------
# #     # User-facing serialization
# #     # --------------------------------------------------------

# #     def to_dict(self, feature_names=None):
# #         """
# #         Convert the unified explanation into a JSON-ready,
# #         user-facing dictionary.
# #         """

# #         names = feature_names or self.feature_names

# #         cai_dict = self.cai.to_dict(names)
# #         cce_dict = self.cce.to_dict(names)

# #         return {
# #             "type": "unified_explanation",

# #             "prediction": {
# #                 "current_output": float(
# #                     self.y_fact
# #                 ),
# #                 "target_output": float(
# #                     self.y_foil
# #                 ),
# #                 "achieved_output": float(
# #                     self.cce.y_achieved
# #                 ),
# #             },

# #             "causal_factors": (
# #                 cai_dict["features"][:3]
# #             ),

# #             "counterfactual": {
# #                 "feasible": cce_dict["feasible"],
# #                 "changes": cce_dict["changes"],
# #                 "causal_validity": (
# #                     cce_dict["causal_validity"]
# #                 ),
# #             },

# #             "summary": {
# #                 "top_causal_feature": (
# #                     cai_dict[
# #                         "top_causal_feature"
# #                     ]
# #                 ),
# #                 "top_causal_effect": (
# #                     cai_dict[
# #                         "top_causal_effect"
# #                     ]
# #                 ),
# #             },
# #         }


# # # ============================================================
# # # PUBLIC API
# # # ============================================================

# # __all__ = [
# #     "CCEResult",
# #     "CAIResult",
# #     "UnifiedExplanation",
# # ]
# """
# Structured result objects for CAUSE-XAI.

# The result classes contain computation outputs only. They do not run
# CCE, CAI, or diagnostic algorithms.

# `to_dict()` returns complete user-facing, JSON-ready information.
# Internal ANM latent states, Gaussian-process objects, temporary search
# state, and Monte Carlo noise are intentionally not serialized.

# `to_json()` is a convenience wrapper around `json.dumps(to_dict())`.
# """

# from dataclasses import dataclass
# import json
# from typing import Any, Dict, List, Optional

# import numpy as np


# def _feature_names(names, n):
#     """Validate/construct the feature-name list."""
#     if names is None:
#         return [f"Feature {i + 1}" for i in range(n)]

#     names = list(names)

#     if len(names) != n:
#         raise ValueError(
#             f"feature_names must contain {n} names; got {len(names)}."
#         )

#     return names


# def _json_value(value):
#     """Recursively convert NumPy/Python values into JSON-safe values."""
#     if value is None:
#         return None

#     if isinstance(value, np.ndarray):
#         return [_json_value(v) for v in value.tolist()]

#     if isinstance(value, (np.integer,)):
#         return int(value)

#     if isinstance(value, (np.floating,)):
#         return float(value)

#     if isinstance(value, (np.bool_,)):
#         return bool(value)

#     if isinstance(value, dict):
#         return {
#             str(k): _json_value(v)
#             for k, v in value.items()
#         }

#     if isinstance(value, (list, tuple)):
#         return [_json_value(v) for v in value]

#     return value


# def _json_float(value):
#     """Convert a scalar numeric value to a Python float."""
#     arr = np.asarray(value)

#     if arr.size != 1:
#         raise ValueError(
#             "Expected a scalar value, but received an array "
#             f"with shape {arr.shape}."
#         )

#     return float(arr.reshape(-1)[0])


# def _json_array(value):
#     return _json_value(np.asarray(value))


# # ============================================================
# # CCE RESULT
# # ============================================================

# @dataclass
# class CCEResult:
#     """Complete Causal Counterfactual Explanation result."""

#     x_obs: np.ndarray
#     x_star: np.ndarray

#     # Internal ANM latent representations.
#     u_obs: np.ndarray
#     u_star: np.ndarray

#     y_fact: float
#     y_foil: float
#     y_achieved: float

#     violation: float
#     d_causal: float
#     sparsity: float

#     changed: List[int]

#     runtime: float
#     feasible: bool

#     direct_interventions: Optional[List[int]] = None

#     # Verified CCE search diagnostics.
#     search_feasible: Optional[bool] = None
#     target_reached: Optional[bool] = None
#     boundary_crossed: Optional[bool] = None
#     y_interventional: Optional[float] = None
#     y_baseline_expectation: Optional[float] = None
#     target_prob: Optional[float] = None
#     search_feasibility: Optional[str] = None

#     def summary(self, feature_names=None):
#         from .display import show_counterfactual

#         show_counterfactual(
#             self,
#             feature_names=feature_names,
#         )

#     def to_dict(self, feature_names=None):
#         """
#         Return the complete user-facing CCE result.

#         Latent `u_obs` and `u_star` are deliberately excluded because
#         they are internal ANM representations rather than user-facing
#         feature values.
#         """
#         names = _feature_names(
#             feature_names,
#             len(self.x_obs),
#         )

#         direct = [
#             int(i)
#             for i in (self.direct_interventions or [])
#         ]

#         changed = [
#             int(i)
#             for i in (self.changed or [])
#         ]

#         downstream = [
#             i for i in changed
#             if i not in direct
#         ]

#         def change_record(index):
#             return {
#                 "feature_index": int(index),
#                 "feature": names[index],
#                 "current_value": _json_float(
#                     self.x_obs[index]
#                 ),
#                 "new_value": _json_float(
#                     self.x_star[index]
#                 ),
#                 "change": _json_float(
#                     self.x_star[index] - self.x_obs[index]
#                 ),
#             }

#         direct_changes = [
#             change_record(i)
#             for i in direct
#             if 0 <= i < len(self.x_obs)
#         ]

#         downstream_changes = [
#             change_record(i)
#             for i in downstream
#             if 0 <= i < len(self.x_obs)
#         ]

#         all_changes = [
#             change_record(i)
#             for i in changed
#             if 0 <= i < len(self.x_obs)
#         ]

#         search = {
#             "search_feasible": (
#                 None
#                 if self.search_feasible is None
#                 else bool(self.search_feasible)
#             ),
#             "target_reached": (
#                 None
#                 if self.target_reached is None
#                 else bool(self.target_reached)
#             ),
#             "boundary_crossed": (
#                 None
#                 if self.boundary_crossed is None
#                 else bool(self.boundary_crossed)
#             ),
#             "target_probability": (
#                 None
#                 if self.target_prob is None
#                 else _json_float(self.target_prob)
#             ),
#             "search_feasibility": self.search_feasibility,
#             "interventional_output": (
#                 None
#                 if self.y_interventional is None
#                 else _json_float(self.y_interventional)
#             ),
#             "baseline_expectation": (
#                 None
#                 if self.y_baseline_expectation is None
#                 else _json_float(
#                     self.y_baseline_expectation
#                 )
#             ),
#         }

#         return {
#             "type": "counterfactual",

#             "observation": {
#                 "feature_values": {
#                     names[i]: _json_float(self.x_obs[i])
#                     for i in range(len(self.x_obs))
#                 },
#                 "vector": _json_array(self.x_obs),
#             },

#             "counterfactual": {
#                 "feature_values": {
#                     names[i]: _json_float(self.x_star[i])
#                     for i in range(len(self.x_star))
#                 },
#                 "vector": _json_array(self.x_star),
#             },

#             "prediction": {
#                 "current_output": _json_float(self.y_fact),
#                 "target_output": _json_float(self.y_foil),
#                 "achieved_output": _json_float(
#                     self.y_achieved
#                 ),
#             },

#             "feasibility": {
#                 "feasible": bool(self.feasible),
#                 "search": search,
#             },

#             "direct_interventions": direct_changes,
#             "downstream_changes": downstream_changes,
#             "changed_features": all_changes,

#             "causal_validity": {
#                 "consistent": bool(
#                     self.violation < 1.5
#                 ),
#                 "violation": _json_float(
#                     self.violation
#                 ),
#                 "causal_distance": _json_float(
#                     self.d_causal
#                 ),
#                 "causal_sparsity": _json_float(
#                     self.sparsity
#                 ),
#             },

#             "metrics": {
#                 "causal_distance": _json_float(
#                     self.d_causal
#                 ),
#                 "causal_sparsity": _json_float(
#                     self.sparsity
#                 ),
#                 "violation": _json_float(
#                     self.violation
#                 ),
#                 "runtime_seconds": _json_float(
#                     self.runtime
#                 ),
#                 "number_of_direct_interventions": len(
#                     direct_changes
#                 ),
#                 "number_of_changed_features": len(
#                     all_changes
#                 ),
#                 "number_of_downstream_changes": len(
#                     downstream_changes
#                 ),
#             },
#         }

#     def to_json(self, feature_names=None, indent=2):
#         """Return the complete user-facing CCE result as a JSON string."""
#         return json.dumps(
#             self.to_dict(feature_names),
#             indent=indent,
#             allow_nan=False,
#         )


# # ============================================================
# # CAI RESULT
# # ============================================================

# @dataclass
# class CAIResult:
#     """Complete Causal Attribution via Interventions result."""

#     x_obs: np.ndarray

#     cai: np.ndarray
#     cai_norm: np.ndarray

#     baseline: float
#     f_do: np.ndarray

#     feature_names: Optional[List[str]] = None

#     standard_errors: Optional[np.ndarray] = None
#     confidence_intervals: Optional[np.ndarray] = None

#     intervention_values: Optional[list] = None
#     n_samples: Optional[int] = None

#     # CRN/uncertainty diagnostics.
#     unpaired_standard_errors: Optional[np.ndarray] = None
#     variance_reduction: Optional[np.ndarray] = None

#     def summary(self, feature_names=None):
#         from .display import show_attribution

#         names = (
#             feature_names
#             if feature_names is not None
#             else self.feature_names
#         )

#         show_attribution(
#             self,
#             feature_names=names,
#         )

#     def to_dict(self, feature_names=None):
#         """
#         Return every feature-level CAI result.

#         No top-k truncation is performed.
#         """
#         names = _feature_names(
#             feature_names
#             if feature_names is not None
#             else self.feature_names,
#             len(self.cai),
#         )

#         features = []

#         for i in range(len(self.cai)):
#             item = {
#                 "feature_index": int(i),
#                 "feature": names[i],
#                 "observed_value": _json_float(
#                     self.x_obs[i]
#                 ),
#                 "causal_effect": _json_float(
#                     self.cai[i]
#                 ),
#                 "normalized_causal_effect": _json_float(
#                     self.cai_norm[i]
#                 ),
#                 "expected_output_do": _json_float(
#                     self.f_do[i]
#                 ),
#             }

#             if (
#                 self.intervention_values is not None
#                 and i < len(self.intervention_values)
#             ):
#                 value = np.asarray(
#                     self.intervention_values[i]
#                 )

#                 if value.size != 1:
#                     raise ValueError(
#                         "CAI intervention_values must contain "
#                         "one scalar value per feature."
#                     )

#                 item["intervention"] = _json_float(
#                     value
#                 )

#             if (
#                 self.standard_errors is not None
#                 and i < len(self.standard_errors)
#             ):
#                 item["standard_error"] = _json_float(
#                     self.standard_errors[i]
#                 )

#             if (
#                 self.confidence_intervals is not None
#                 and i < len(self.confidence_intervals)
#             ):
#                 ci = np.asarray(
#                     self.confidence_intervals[i]
#                 ).reshape(-1)

#                 if ci.size >= 2:
#                     item["confidence_interval_95"] = [
#                         float(ci[0]),
#                         float(ci[1]),
#                     ]

#             if (
#                 self.unpaired_standard_errors is not None
#                 and i < len(
#                     self.unpaired_standard_errors
#                 )
#             ):
#                 item[
#                     "unpaired_standard_error"
#                 ] = _json_float(
#                     self.unpaired_standard_errors[i]
#                 )

#             if (
#                 self.variance_reduction is not None
#                 and i < len(self.variance_reduction)
#             ):
#                 item[
#                     "variance_reduction"
#                 ] = _json_float(
#                     self.variance_reduction[i]
#                 )

#             features.append(item)

#         order = np.argsort(
#             np.abs(self.cai)
#         )[::-1]

#         ranking = [
#             {
#                 "rank": rank + 1,
#                 "feature_index": int(index),
#                 "feature": names[int(index)],
#                 "causal_effect": _json_float(
#                     self.cai[int(index)]
#                 ),
#                 "absolute_causal_effect": _json_float(
#                     abs(self.cai[int(index)])
#                 ),
#             }
#             for rank, index in enumerate(order)
#         ]

#         top_index = (
#             int(order[0])
#             if len(order) > 0
#             else None
#         )

#         return {
#             "type": "causal_attribution",

#             "observation": {
#                 "feature_values": {
#                     names[i]: _json_float(
#                         self.x_obs[i]
#                     )
#                     for i in range(len(self.x_obs))
#                 },
#                 "vector": _json_array(self.x_obs),
#             },

#             "baseline_output": _json_float(
#                 self.baseline
#             ),

#             "monte_carlo": {
#                 "n_samples": (
#                     None
#                     if self.n_samples is None
#                     else int(self.n_samples)
#                 ),
#                 "common_random_numbers": True,
#                 "uncertainty_method": "paired",
#                 "confidence_level": 0.95,
#             },

#             "features": features,

#             "ranking": {
#                 "by_absolute_causal_effect": ranking
#             },

#             "top_causal_feature": (
#                 names[top_index]
#                 if top_index is not None
#                 else None
#             ),

#             "top_causal_effect": (
#                 _json_float(
#                     self.cai[top_index]
#                 )
#                 if top_index is not None
#                 else None
#             ),
#         }

#     def to_json(self, feature_names=None, indent=2):
#         """Return the complete user-facing CAI result as JSON."""
#         return json.dumps(
#             self.to_dict(feature_names),
#             indent=indent,
#             allow_nan=False,
#         )


# # ============================================================
# # UNIFIED EXPLANATION
# # ============================================================

# @dataclass
# class UnifiedExplanation:
#     """
#     Complete explanation for one observation.

#     Contains CCE + CAI and, when produced by `explain_all()`, the
#     complete CAI-vs-SHAP-style diagnostic comparison.
#     """

#     x_obs: np.ndarray
#     y_fact: float
#     y_foil: float

#     cce: CCEResult
#     cai: CAIResult

#     feature_names: Optional[List[str]] = None

#     # Optional output of diagnostics.compare_cai_shap().
#     comparison: Optional[Dict[str, Any]] = None

#     def summary(self, feature_names=None):
#         from .display import show_explanation

#         names = (
#             feature_names
#             if feature_names is not None
#             else self.feature_names
#         )

#         show_explanation(
#             self,
#             feature_names=names,
#         )

#     @staticmethod
#     def _comparison_to_dict(
#         comparison,
#         feature_names,
#     ):
#         if comparison is None:
#             return None

#         names = list(feature_names)

#         result = {}

#         scalar_keys = (
#             "baseline_int",
#             "baseline_obs",
#             "n_biased",
#             "bias_threshold",
#             "bias_rate",
#             "mean_abs_difference",
#             "max_abs_difference",
#         )

#         for key in scalar_keys:
#             if key in comparison:
#                 result[key] = _json_value(
#                     comparison[key]
#                 )

#         cai = comparison.get("cai")
#         shap = comparison.get("shap_style")
#         difference = comparison.get("difference")

#         if cai is not None:
#             cai = np.asarray(cai, dtype=float)

#         if shap is not None:
#             shap = np.asarray(
#                 shap,
#                 dtype=float,
#             )

#         if (
#             difference is None
#             and cai is not None
#             and shap is not None
#         ):
#             difference = cai - shap

#         if difference is not None:
#             difference = np.asarray(
#                 difference,
#                 dtype=float,
#             )

#         if cai is not None:
#             result["cai_interventional"] = _json_array(
#                 cai
#             )

#         if shap is not None:
#             result[
#                 "shap_style_observational"
#             ] = _json_array(shap)

#         if difference is not None:
#             result["difference"] = _json_array(
#                 difference
#             )

#         if (
#             cai is not None
#             and shap is not None
#         ):
#             rows = []

#             for i in range(len(cai)):
#                 row = {
#                     "feature_index": int(i),
#                     "feature": names[i],
#                     "cai_interventional": float(
#                         cai[i]
#                     ),
#                     "shap_style_observational": float(
#                         shap[i]
#                     ),
#                 }

#                 if difference is not None:
#                     row["difference"] = float(
#                         difference[i]
#                     )

#                 if (
#                     "bias_threshold" in comparison
#                     and difference is not None
#                 ):
#                     row["biased"] = bool(
#                         abs(difference[i])
#                         > float(
#                             comparison[
#                                 "bias_threshold"
#                             ]
#                         )
#                     )

#                 rows.append(row)

#             result["features"] = rows

#         return result

#     def to_dict(self, feature_names=None):
#         """
#         Return the complete user-facing explanation.

#         This contains all feature-level CAI information and all CCE
#         search information. It does not truncate the result to a
#         top-three summary.
#         """
#         names = _feature_names(
#             feature_names
#             if feature_names is not None
#             else self.feature_names,
#             len(self.x_obs),
#         )

#         cce_dict = self.cce.to_dict(names)
#         cai_dict = self.cai.to_dict(names)

#         direct_count = len(
#             self.cce.direct_interventions or []
#         )

#         changed = self.cce.changed or []
#         direct = set(
#             self.cce.direct_interventions or []
#         )

#         downstream_count = sum(
#             1 for i in changed
#             if i not in direct
#         )

#         return {
#             "type": "unified_explanation",

#             "observation": {
#                 "feature_values": {
#                     names[i]: _json_float(
#                         self.x_obs[i]
#                     )
#                     for i in range(len(self.x_obs))
#                 },
#                 "vector": _json_array(self.x_obs),
#             },

#             "prediction": {
#                 "current_output": _json_float(
#                     self.y_fact
#                 ),
#                 "target_output": _json_float(
#                     self.y_foil
#                 ),
#                 "achieved_output": _json_float(
#                     self.cce.y_achieved
#                 ),
#             },

#             # Complete nested results.
#             "counterfactual": cce_dict,
#             "causal_attribution": cai_dict,

#             # Convenient aliases for applications.
#             "causal_factors": cai_dict[
#                 "features"
#             ],

#             "comparison": self._comparison_to_dict(
#                 self.comparison,
#                 names,
#             ),

#             "summary": {
#                 "feasible": bool(
#                     self.cce.feasible
#                 ),
#                 "target_reached": (
#                     None
#                     if self.cce.target_reached is None
#                     else bool(
#                         self.cce.target_reached
#                     )
#                 ),
#                 "top_causal_feature": (
#                     cai_dict[
#                         "top_causal_feature"
#                     ]
#                 ),
#                 "top_causal_effect": (
#                     cai_dict[
#                         "top_causal_effect"
#                     ]
#                 ),
#                 "number_of_direct_interventions": (
#                     direct_count
#                 ),
#                 "number_of_downstream_changes": (
#                     downstream_count
#                 ),
#                 "number_of_features": len(
#                     names
#                 ),
#             },
#         }

#     def to_json(self, feature_names=None, indent=2):
#         """
#         Return the complete unified explanation as a JSON string.

#         Example
#         -------
#         json_text = explanation.to_json()
#         """
#         return json.dumps(
#             self.to_dict(feature_names),
#             indent=indent,
#             allow_nan=False,
#         )


# __all__ = [
#     "CCEResult",
#     "CAIResult",
#     "UnifiedExplanation",
# ]


"""Structured results for the verified CCE-ANM pipeline."""

from dataclasses import dataclass
import json
from typing import Any, Dict, List, Optional

import numpy as np


def _feature_names(names, n):
    if names is None:
        return [f"Feature {i + 1}" for i in range(n)]

    names = list(names)

    if len(names) != n:
        raise ValueError(
            f"feature_names must contain {n} names; "
            f"got {len(names)}."
        )

    return names


def _json_value(value):
    if value is None:
        return None

    if isinstance(value, np.ndarray):
        return [
            _json_value(v)
            for v in value.tolist()
        ]

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        return float(value)

    if isinstance(value, np.bool_):
        return bool(value)

    if isinstance(value, dict):
        return {
            str(k): _json_value(v)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _json_value(v)
            for v in value
        ]

    return value


def _json_float(value):
    arr = np.asarray(value)

    if arr.size != 1:
        raise ValueError(
            "Expected a scalar value, but received "
            f"an array with shape {arr.shape}."
        )

    return float(
        arr.reshape(-1)[0]
    )


@dataclass
class CCEResult:
    x_obs: np.ndarray
    x_star: np.ndarray
    u_obs: np.ndarray
    u_star: np.ndarray
    y_fact: float
    y_foil: float
    y_achieved: float
    violation: float
    d_causal: float
    sparsity: float
    changed: list
    runtime: float
    feasible: bool
    direct_interventions: list = None
    y_interventional: float = None
    boundary_crossed: bool = False
    target_reached: bool = False
    search_feasibility: str = "instance"
    search_feasible: bool = False
    target_prob: float = 0.55
    y_baseline_expectation: float = None

    def summary(self, names=None):
        from .display import show_counterfactual
        show_counterfactual(
            self,
            feature_names=names,
        )

    def to_dict(self, feature_names=None):
        names = _feature_names(
            feature_names,
            len(self.x_obs),
        )

        direct = [
            int(i)
            for i in (self.direct_interventions or [])
        ]

        changed = [
            int(i)
            for i in (self.changed or [])
        ]

        downstream = [
            i for i in changed
            if i not in direct
        ]

        def change_record(index):
            return {
                "feature_index": int(index),
                "feature": names[index],
                "current_value": _json_float(
                    self.x_obs[index]
                ),
                "new_value": _json_float(
                    self.x_star[index]
                ),
                "change": _json_float(
                    self.x_star[index]
                    - self.x_obs[index]
                ),
            }

        return {
            "observation": {
                "values": _json_value(
                    self.x_obs
                ),
                "features": {
                    names[i]: _json_float(
                        self.x_obs[i]
                    )
                    for i in range(
                        len(self.x_obs)
                    )
                },
            },
            "counterfactual": {
                "values": _json_value(
                    self.x_star
                ),
                "features": {
                    names[i]: _json_float(
                        self.x_star[i]
                    )
                    for i in range(
                        len(self.x_star)
                    )
                },
            },
            "prediction": {
                "current": _json_float(
                    self.y_fact
                ),
                "target_class": int(
                    self.y_foil
                ),
                "achieved": _json_float(
                    self.y_achieved
                ),
            },
            "feasibility": {
                "feasible": bool(
                    self.feasible
                ),
                "search_feasible": bool(
                    self.search_feasible
                ),
                "target_reached": bool(
                    self.target_reached
                ),
                "boundary_crossed": bool(
                    self.boundary_crossed
                ),
                "target_probability": _json_float(
                    self.target_prob
                ),
                "search_feasibility": (
                    self.search_feasibility
                ),
            },
            "direct_interventions": [
                change_record(i)
                for i in direct
                if 0 <= i < len(self.x_obs)
            ],
            "downstream_changes": [
                change_record(i)
                for i in downstream
                if 0 <= i < len(self.x_obs)
            ],
            "changed_features": [
                change_record(i)
                for i in changed
                if 0 <= i < len(self.x_obs)
            ],
            "causal_validity": {
                "violation": _json_float(
                    self.violation
                ),
                "causal_distance": _json_float(
                    self.d_causal
                ),
                "causal_sparsity": _json_float(
                    self.sparsity
                ),
            },
            "search_diagnostics": {
                "interventional_output": (
                    None
                    if self.y_interventional is None
                    else _json_float(
                        self.y_interventional
                    )
                ),
                "baseline_expectation": (
                    None
                    if self.y_baseline_expectation is None
                    else _json_float(
                        self.y_baseline_expectation
                    )
                ),
            },
            "runtime_seconds": _json_float(
                self.runtime
            ),
        }

    def to_json(self, feature_names=None, indent=2):
        return json.dumps(
            self.to_dict(feature_names),
            indent=indent,
            allow_nan=False,
        )


@dataclass
class CAIResult:
    x_obs: np.ndarray
    cai: np.ndarray
    cai_norm: np.ndarray
    baseline: float
    f_do: np.ndarray
    feature_names: list = None
    standard_errors: np.ndarray = None
    confidence_intervals: np.ndarray = None
    intervention_values: list = None
    n_samples: int = None
    unpaired_standard_errors: np.ndarray = None
    variance_reduction_ratios: np.ndarray = None

    def summary(self):
        from .display import show_attribution
        show_attribution(
            self,
            feature_names=self.feature_names,
        )

    def to_dict(self, feature_names=None):
        names = _feature_names(
            feature_names
            if feature_names is not None
            else self.feature_names,
            len(self.cai),
        )

        features = []

        for i in range(len(self.cai)):
            item = {
                "feature_index": int(i),
                "feature": names[i],
                "observed_value": _json_float(
                    self.x_obs[i]
                ),
                "causal_effect": _json_float(
                    self.cai[i]
                ),
                "normalized_causal_effect": _json_float(
                    self.cai_norm[i]
                ),
                "expected_output_do": _json_float(
                    self.f_do[i]
                ),
            }

            if (
                self.intervention_values is not None
                and i < len(self.intervention_values)
            ):
                item["intervention"] = _json_float(
                    self.intervention_values[i]
                )

            if (
                self.standard_errors is not None
                and i < len(self.standard_errors)
            ):
                item["standard_error"] = _json_float(
                    self.standard_errors[i]
                )

            if (
                self.confidence_intervals is not None
                and i < len(
                    self.confidence_intervals
                )
            ):
                ci = np.asarray(
                    self.confidence_intervals[i]
                ).reshape(-1)

                if ci.size >= 2:
                    item[
                        "confidence_interval_95"
                    ] = [
                        float(ci[0]),
                        float(ci[1]),
                    ]

            if (
                self.unpaired_standard_errors
                is not None
            ):
                item[
                    "unpaired_standard_error"
                ] = _json_float(
                    self.unpaired_standard_errors[i]
                )

            if (
                self.variance_reduction_ratios
                is not None
            ):
                item[
                    "variance_reduction_ratio"
                ] = _json_float(
                    self.variance_reduction_ratios[i]
                )

            features.append(item)

        order = np.argsort(
            np.abs(self.cai)
        )[::-1]

        return {
            "observation": {
                "values": _json_value(
                    self.x_obs
                ),
            },
            "baseline_expected_output": _json_float(
                self.baseline
            ),
            "monte_carlo_samples": (
                None
                if self.n_samples is None
                else int(self.n_samples)
            ),
            "features": features,
            "ranking": [
                {
                    "rank": int(rank + 1),
                    "feature_index": int(i),
                    "feature": names[i],
                    "causal_effect": _json_float(
                        self.cai[i]
                    ),
                }
                for rank, i in enumerate(order)
            ],
            "top_feature": (
                None
                if len(order) == 0
                else names[int(order[0])]
            ),
            "top_causal_effect": (
                None
                if len(order) == 0
                else _json_float(
                    self.cai[int(order[0])]
                )
            ),
        }

    def to_json(self, feature_names=None, indent=2):
        return json.dumps(
            self.to_dict(feature_names),
            indent=indent,
            allow_nan=False,
        )


@dataclass
class UnifiedExplanation:
    x_obs: np.ndarray
    y_fact: float
    y_foil: float
    cce: CCEResult
    cai: CAIResult
    feature_names: list = None
    comparison: dict = None

    def summary(self, feature_names=None):
        from .display import show_explanation
        show_explanation(
            self,
            feature_names=(
                feature_names
                if feature_names is not None
                else self.feature_names
            ),
        )

    def to_dict(self, feature_names=None):
        names = (
            feature_names
            if feature_names is not None
            else self.feature_names
        )

        cce = self.cce.to_dict(names)
        cai = self.cai.to_dict(names)

        causal_factors = []

        for rank, index in enumerate(
            np.argsort(
                np.abs(self.cai.cai)
            )[::-1],
            start=1,
        ):
            index = int(index)

            causal_factors.append({
                "rank": rank,
                "feature_index": index,
                "feature": (
                    names[index]
                    if names is not None
                    else f"Feature {index + 1}"
                ),
                "causal_effect": _json_float(
                    self.cai.cai[index]
                ),
            })

        comparison = (
            None
            if self.comparison is None
            else _json_value(self.comparison)
        )

        return {
            "observation": {
                "values": _json_value(
                    self.x_obs
                ),
            },
            "prediction": {
                "current": _json_float(
                    self.y_fact
                ),
                "target_class": int(
                    self.y_foil
                ),
                "achieved": _json_float(
                    self.cce.y_achieved
                ),
            },
            "counterfactual": cce,
            "causal_attribution": cai,
            "causal_factors": causal_factors,
            "comparison": comparison,
            "summary": {
                "feasible": bool(
                    self.cce.feasible
                ),
                "top_causal_feature": (
                    causal_factors[0]["feature"]
                    if causal_factors
                    else None
                ),
                "top_causal_effect": (
                    causal_factors[0][
                        "causal_effect"
                    ]
                    if causal_factors
                    else None
                ),
            },
        }

    def to_json(self, feature_names=None, indent=2):
        return json.dumps(
            self.to_dict(feature_names),
            indent=indent,
            allow_nan=False,
        )


__all__ = [
    "CCEResult",
    "CAIResult",
    "UnifiedExplanation",
]
