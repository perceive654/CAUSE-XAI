
# # # import numpy as np
# # # import time

# # # from .config import TARGET_PROB
# # # from .results import CCEResult
# # # from .cai import attribute_cai

# # # def counterfactual_search(
# # #     model,
# # #     x_obs,
# # #     y_foil,
# # #     non_actionable=None,
# # #     verbose=False,
# # # ):
# # #     """
# # #     Find a causal counterfactual x* = Φ(u*) that:
# # #       1. reaches the target class y_foil (0 or 1), and
# # #       2. minimizes causal/proximity distance among feasible solutions.

# # #     This mirrors the CCE-ANM notebook implementation.

# # #     Parameters
# # #     ----------
# # #     model : CCE_ANM_Model
# # #         Fitted model with attributes:
# # #           - anm_
# # #           - sigma_
# # #           - _f
# # #           - K_cce
# # #           - top_k
# # #           - lambda_

# # #     x_obs : np.ndarray
# # #         Instance to explain (shape (p,)).

# # #     y_foil : int
# # #         Target class (0 or 1).

# # #     verbose : bool
# # #         Whether to print progress.

# # #     Returns
# # #     -------
# # #     CCEResult
# # #     """
    
# # #     t0 = time.time()

# # #     x_obs = np.asarray(x_obs, dtype=float)

# # #     anm = model.anm_
# # #     sigma = np.asarray(model.sigma_, dtype=float)

# # #     target_prob = TARGET_PROB

# # #     # ------------------------------------------------------------
# # #     # 1. Observed point in ANM noise space
# # #     # ------------------------------------------------------------
# # #     u_obs = anm.inverse(x_obs)

# # #     # ------------------------------------------------------------
# # #     # 2. Factual prediction
# # #     # ------------------------------------------------------------
# # #     x_obs_2d = x_obs.reshape(1, -1)

# # #     p_out = model._f(x_obs_2d)

# # #     if p_out.ndim == 2:
# # #         y_fact = float(p_out[0, 1])
# # #     else:
# # #         y_fact = float(p_out[0])

# # #     if non_actionable is None:
# # #         non_actionable = []

# # #     non_actionable_idx = []

# # #     for feature in non_actionable:
# # #         if isinstance(feature, str):
# # #             non_actionable_idx.append(
# # #                 model.feature_names.index(feature)
# # #             )
# # #         else:
# # #             non_actionable_idx.append(int(feature))

# # #     # ------------------------------------------------------------
# # #     # 3. CAI-guided intervention ranking
# # #     # ------------------------------------------------------------
# # #     # cai = model.attribute(
# # #     #     x_obs,
# # #     #     feature_names=None,
# # #     #     verbose=False,
# # #     # ).cai

# # #     cai_result = attribute_cai(
# # #         model,
# # #         x_obs,
# # #         feature_names=model.feature_names,
# # #         verbose=False,
# # #     )

# # #     cai = cai_result.cai

# # #     # top_idx = np.argsort(
# # #     #     np.abs(cai)
# # #     # )[::-1][:model.top_k]

# # #     top_idx = [
# # #         i for i in np.argsort(np.abs(cai))[::-1]
# # #         if i not in non_actionable_idx
# # #     ][:model.top_k]

# # #     if verbose:
# # #         print("\nOptimizing only:")
# # #         print(
# # #             "  "
# # #             + "  ".join(
# # #                 f"X{j + 1}"
# # #                 for j in top_idx
# # #             )
# # #         )

# # #     # ------------------------------------------------------------
# # #     # 4. Fixed Monte-Carlo noise
# # #     # ------------------------------------------------------------
# # #     rng = np.random.default_rng(42)

# # #     fixed_noise = {}

# # #     for j in anm.order:

# # #         loc, sc = anm.noise[j]

# # #         fixed_noise[j] = rng.laplace(
# # #             loc=loc,
# # #             scale=sc,
# # #             size=model.K_cce,
# # #         )

# # #     # ------------------------------------------------------------
# # #     # 5. Interventional prediction
# # #     # ------------------------------------------------------------
# # #     def f_int(xp, intervention_idx):
# # #         """
# # #         Estimate:

# # #             E[f(X) | do(X_S = x_S)]

# # #         using the fitted ANM.
# # #         """

# # #         intervention_idx = np.asarray(
# # #             intervention_idx,
# # #             dtype=int,
# # #         )

# # #         S = {
# # #             int(j): float(xp[j])
# # #             for j in intervention_idx
# # #         }

# # #         samp = np.zeros(
# # #             (model.K_cce, anm.p),
# # #             dtype=float,
# # #         )

# # #         intervened = set(
# # #             S.keys()
# # #         )

# # #         for j in anm.order:

# # #             if j in intervened:

# # #                 samp[:, j] = S[j]

# # #             else:

# # #                 eq = anm.eqs[j]

# # #                 if eq.is_root:

# # #                     g = np.zeros(
# # #                         model.K_cce
# # #                     )

# # #                 else:

# # #                     g = eq.predict(
# # #                         samp[:, eq.parents]
# # #                     )

# # #                 samp[:, j] = (
# # #                     g + fixed_noise[j]
# # #                 )

# # #         preds = model._f(samp)

# # #         if preds.ndim == 2:

# # #             return float(
# # #                 preds[:, 1].mean()
# # #             )

# # #         return float(
# # #             preds.mean()
# # #         )

# # #     # ------------------------------------------------------------
# # #     # 6. Target-condition helper
# # #     # ------------------------------------------------------------
# # #     def target_reached(prediction):
# # #         """
# # #         Check whether the requested target class has been reached.

# # #         For class 1:
# # #             P(Y=1) >= TARGET_PROB

# # #         For class 0:
# # #             P(Y=0) >= TARGET_PROB
# # #             equivalent to
# # #             P(Y=1) <= 1 - TARGET_PROB
# # #         """

# # #         if int(y_foil) == 1:

# # #             return (
# # #                 prediction >= target_prob
# # #             )

# # #         if int(y_foil) == 0:

# # #             return (
# # #                 prediction
# # #                 <= (1.0 - target_prob)
# # #             )

# # #         raise ValueError(
# # #             "y_foil must be either 0 or 1"
# # #         )

# # #     # ------------------------------------------------------------
# # #     # 7. Causal/proximity distance
# # #     # ------------------------------------------------------------
# # #     def causal_distance(u_candidate):

# # #         x_candidate = anm.forward(
# # #             u_candidate
# # #         )

# # #         prox = float(
# # #             np.sum(
# # #                 np.abs(
# # #                     x_obs - x_candidate
# # #                 )
# # #                 / (
# # #                     sigma + 1e-8
# # #                 )
# # #             )
# # #         )

# # #         caus = float(
# # #             model.lambda_
# # #             * np.sum(
# # #                 (
# # #                     u_candidate
# # #                     - u_obs
# # #                 ) ** 2
# # #             )
# # #         )

# # #         return prox + caus

# # #     # ------------------------------------------------------------
# # #     # 8. Search for minimum intervention
# # #     # ------------------------------------------------------------
# # #     def find_minimal_intervention(
# # #         active_idx
# # #     ):

# # #         u_base = u_obs.copy()

# # #         x_base = anm.forward(
# # #             u_base
# # #         )

# # #         base_pred = f_int(
# # #             x_base,
# # #             active_idx,
# # #         )

# # #         if target_reached(
# # #             base_pred
# # #         ):

# # #             return (
# # #                 u_base.copy(),
# # #                 base_pred,
# # #             )

# # #         max_step = 3.0
# # #         n_steps = 30

# # #         best_solution = None
# # #         best_distance = np.inf
# # #         best_prediction = base_pred

# # #         # Search in both directions
# # #         # in latent/noise space.
# # #         for direction in (
# # #             1.0,
# # #             -1.0,
# # #         ):

# # #             low = 0.0
# # #             high = max_step
# # #             found = False

# # #             # ----------------------------------------------------
# # #             # Coarse search
# # #             # ----------------------------------------------------
# # #             for step in np.linspace(
# # #                 0.05,
# # #                 max_step,
# # #                 n_steps,
# # #             ):

# # #                 u_test = u_obs.copy()

# # #                 u_test[active_idx] = (
# # #                     u_obs[active_idx]
# # #                     + direction * step
# # #                 )

# # #                 x_test = anm.forward(
# # #                     u_test
# # #                 )

# # #                 pred_test = f_int(
# # #                     x_test,
# # #                     active_idx,
# # #                 )

# # #                 if target_reached(
# # #                     pred_test
# # #                 ):

# # #                     high = step
# # #                     found = True
# # #                     break

# # #                 low = step

# # #             if not found:
# # #                 continue

# # #             # ----------------------------------------------------
# # #             # Binary refinement
# # #             # ----------------------------------------------------
# # #             for _ in range(25):

# # #                 mid = (
# # #                     low + high
# # #                 ) / 2.0

# # #                 u_test = u_obs.copy()

# # #                 u_test[active_idx] = (
# # #                     u_obs[active_idx]
# # #                     + direction * mid
# # #                 )

# # #                 x_test = anm.forward(
# # #                     u_test
# # #                 )

# # #                 pred_test = f_int(
# # #                     x_test,
# # #                     active_idx,
# # #                 )

# # #                 if target_reached(
# # #                     pred_test
# # #                 ):

# # #                     high = mid

# # #                 else:

# # #                     low = mid

# # #             # ----------------------------------------------------
# # #             # Final candidate
# # #             # ----------------------------------------------------
# # #             u_candidate = u_obs.copy()

# # #             u_candidate[active_idx] = (
# # #                 u_obs[active_idx]
# # #                 + direction * high
# # #             )

# # #             x_candidate = anm.forward(
# # #                 u_candidate
# # #             )

# # #             pred_candidate = f_int(
# # #                 x_candidate,
# # #                 active_idx,
# # #             )

# # #             distance = causal_distance(
# # #                 u_candidate
# # #             )

# # #             if (
# # #                 target_reached(
# # #                     pred_candidate
# # #                 )
# # #                 and distance < best_distance
# # #             ):

# # #                 best_solution = (
# # #                     u_candidate.copy()
# # #                 )

# # #                 best_distance = (
# # #                     distance
# # #                 )

# # #                 best_prediction = (
# # #                     pred_candidate
# # #                 )

# # #         return (
# # #             best_solution,
# # #             best_prediction,
# # #         )

# # #     # ------------------------------------------------------------
# # #     # 9. Progressive sparse search
# # #     # ------------------------------------------------------------
# # #     best_u = None
# # #     best_loss = np.inf
# # #     best_pred = y_fact
# # #     best_k = None
# # #     best_intervention_idx = None

# # #     if verbose:
# # #         print(
# # #             "\n[CCE] Progressive sparse search..."
# # #         )

# # #     for k in range(
# # #         1,
# # #         len(top_idx) + 1,
# # #     ):

# # #         active_idx = top_idx[:k]

# # #         if verbose:

# # #             print(
# # #                 f"\n  Trying {k} intervention "
# # #                 f"variable(s): "
# # #                 + " ".join(
# # #                     f"X{j + 1}"
# # #                     for j in active_idx
# # #                 )
# # #             )

# # #         (
# # #             u_candidate,
# # #             pred_candidate,
# # #         ) = find_minimal_intervention(
# # #             active_idx
# # #         )

# # #         if u_candidate is None:

# # #             if verbose:

# # #                 print(
# # #                     "    No feasible solution"
# # #                 )

# # #             continue

# # #         x_candidate = anm.forward(
# # #             u_candidate
# # #         )

# # #         pred_candidate = f_int(
# # #             x_candidate,
# # #             active_idx,
# # #         )

# # #         candidate_distance = (
# # #             causal_distance(
# # #                 u_candidate
# # #             )
# # #         )

# # #         feasible = target_reached(
# # #             pred_candidate
# # #         )

# # #         if verbose:

# # #             print(
# # #                 f"    f_int={pred_candidate:.3f} "
# # #                 f"distance={candidate_distance:.4f} "
# # #                 f"feasible={feasible}"
# # #             )

# # #         if feasible:

# # #             if (
# # #                 best_u is None
# # #                 or k < best_k
# # #                 or (
# # #                     k == best_k
# # #                     and candidate_distance
# # #                     < best_loss
# # #                 )
# # #             ):

# # #                 best_u = (
# # #                     u_candidate.copy()
# # #                 )

# # #                 best_loss = (
# # #                     candidate_distance
# # #                 )

# # #                 best_pred = (
# # #                     pred_candidate
# # #                 )

# # #                 best_k = k

# # #                 best_intervention_idx = (
# # #                     active_idx.copy()
# # #                 )

# # #         # Stop as soon as the sparsest
# # #         # feasible intervention set is found.
# # #         if best_u is not None:

# # #             if verbose:

# # #                 print(
# # #                     f"\n[CCE] Sparse solution found "
# # #                     f"with {best_k} "
# # #                     f"intervention variable(s)."
# # #                 )

# # #             break

# # #     # ------------------------------------------------------------
# # #     # 10. No feasible counterfactual
# # #     # ------------------------------------------------------------
# # #     if best_u is None:

# # #         if verbose:

# # #             print(
# # #                 "\n[CCE] No feasible counterfactual "
# # #                 "found within selected "
# # #                 "intervention variables."
# # #             )

# # #         best_u = u_obs.copy()

# # #         x_star = anm.forward(
# # #             best_u
# # #         )

# # #         y_ach = y_fact

# # #         viol = anm.violation(
# # #             x_star
# # #         )

# # #         return CCEResult(
# # #             x_obs=x_obs,
# # #             x_star=x_star,
# # #             u_obs=u_obs,
# # #             u_star=best_u,
# # #             y_fact=y_fact,
# # #             y_foil=y_foil,
# # #             y_achieved=y_ach,
# # #             violation=viol,
# # #             d_causal=0.0,
# # #             sparsity=1.0,
# # #             changed=[],
# # #             direct_interventions=[],
# # #             runtime=time.time() - t0,
# # #             feasible=False,
# # #         )

# # #     # ------------------------------------------------------------
# # #     # 11. Final counterfactual
# # #     # ------------------------------------------------------------
# # #     x_star = anm.forward(
# # #         best_u
# # #     )

# # #     y_ach = f_int(
# # #         x_star,
# # #         best_intervention_idx,
# # #     )

# # #     # ------------------------------------------------------------
# # #     # 12. Intervention validation
# # #     # ------------------------------------------------------------
# # #     if (
# # #         best_intervention_idx is not None
# # #         and verbose
# # #     ):

# # #         validated_pred = f_int(
# # #             x_star,
# # #             best_intervention_idx,
# # #         )

# # #         print(
# # #             "\n[CCE] Intervention validation:"
# # #         )

# # #         for j in best_intervention_idx:

# # #             print(
# # #                 f"  do(X{j + 1} = "
# # #                 f"{x_obs[j]:.3f} → "
# # #                 f"{x_star[j]:.3f})"
# # #             )

# # #         print(
# # #             f"  Interventional prediction : "
# # #             f"{validated_pred:.4f}"
# # #         )

# # #         print(
# # #             f"  Target boundary           : "
# # #             f"{target_prob:.4f}"
# # #         )

# # #         print(
# # #             f"  Target reached            : "
# # #             f"{target_reached(validated_pred)}"
# # #         )

# # #     # ------------------------------------------------------------
# # #     # 13. Manifold violation
# # #     # ------------------------------------------------------------
# # #     viol = anm.violation(
# # #         x_star
# # #     )

# # #     # ------------------------------------------------------------
# # #     # 14. Direct intervention variables
# # #     # ------------------------------------------------------------
# # #     # intervention_vars = (
# # #     #     best_intervention_idx.tolist()
# # #     #     if best_intervention_idx is not None
# # #     #     else []
# # #     # )

# # #     intervention_vars = (
# # #         list(best_intervention_idx)
# # #         if best_intervention_idx is not None
# # #         else []
# # #     )

# # #     direct_interventions = len(
# # #         intervention_vars
# # #     )

# # #     # ------------------------------------------------------------
# # #     # 15. Downstream observed changes
# # #     # ------------------------------------------------------------
# # #     changed_observed = [
# # #         j
# # #         for j in range(anm.p)
# # #         if (
# # #             j not in intervention_vars
# # #             and abs(
# # #                 x_star[j]
# # #                 - x_obs[j]
# # #             ) > 0.05
# # #         )
# # #     ]

# # #     # ------------------------------------------------------------
# # #     # 16. Causal sparsity
# # #     # ------------------------------------------------------------
# # #     sparsity = (
# # #         1.0
# # #         - direct_interventions
# # #         / anm.p
# # #     )

# # #     # ------------------------------------------------------------
# # #     # 17. Final verbose output
# # #     # ------------------------------------------------------------
# # #     if verbose:

# # #         print(
# # #             "\n[CCE] Best feasible solution:"
# # #         )

# # #         print(
# # #             f"  Prediction : "
# # #             f"{y_fact:.3f} → "
# # #             f"{y_ach:.3f}"
# # #         )

# # #         print(
# # #             f"  Distance   : "
# # #             f"{best_loss:.4f}"
# # #         )

# # #         print(
# # #             f"  V_M        : "
# # #             f"{viol:.4f}"
# # #         )

# # #         print(
# # #             f"  Direct interventions : "
# # #             f"{direct_interventions}"
# # #         )

# # #         print(
# # #             f"  Downstream changes   : "
# # #             f"{len(changed_observed)}"
# # #         )

# # #         print(
# # #             f"  Causal sparsity      : "
# # #             f"{sparsity:.2f}"
# # #         )

# # #     # ------------------------------------------------------------
# # #     # 18. Return CCEResult
# # #     # ------------------------------------------------------------
# # #     return CCEResult(
# # #         x_obs=x_obs,
# # #         x_star=x_star,
# # #         u_obs=u_obs,
# # #         u_star=best_u,
# # #         y_fact=y_fact,
# # #         y_foil=y_foil,
# # #         y_achieved=y_ach,
# # #         violation=viol,
# # #         d_causal=best_loss,
# # #         sparsity=sparsity,
# # #         changed=changed_observed,
# # #         direct_interventions=intervention_vars,
# # #         runtime=time.time() - t0,
# # #         feasible=True,
# # #     )

# # import time

# # import numpy as np

# # from .config import TARGET_PROB
# # from .results import CCEResult
# # from .cai import attribute_cai


# # def counterfactual_search(
# #     model,
# #     x_obs,
# #     y_foil,
# #     non_actionable=None,
# #     verbose=False,
# # ):
# #     """
# #     Search for a causal counterfactual using the verified CCE-ANM
# #     counterfactual algorithm.

# #     The search follows the verified notebook:

# #     1. Map the observation to ANM noise space.
# #     2. Evaluate the factual black-box probability.
# #     3. Rank intervention candidates using CAI.
# #     4. Use a deterministic fixed-noise population simulator.
# #     5. Support two feasibility oracles:
# #        - instance:      f(x*) >= target_prob
# #        - population:    E[f(X) | do(X_S=x_S)] >= target_prob
# #     6. Search progressively over the top-k causal variables.
# #     7. For each active intervention set, search both directions using
# #        a coarse 1-D ray search followed by bisection.
# #     8. Return the sparsest feasible intervention set.

# #     The existing CCE result fields used by the display layer are retained:
# #     x_obs, x_star, u_obs, u_star, y_fact, y_foil, y_achieved,
# #     violation, d_causal, sparsity, changed, direct_interventions,
# #     runtime, and feasible.

# #     Additional result fields introduced by the verified notebook are:
# #     search_feasible, target_reached, boundary_crossed,
# #     y_interventional, y_baseline_expectation, target_prob,
# #     and search_feasibility.
# #     """

# #     t0 = time.time()

# #     x_obs = np.asarray(x_obs, dtype=float).reshape(-1)

# #     anm = model.anm_
# #     sigma = np.asarray(model.sigma_, dtype=float)

# #     target_prob = float(
# #         getattr(model, "target_prob", TARGET_PROB)
# #     )

# #     search_feasibility = getattr(
# #         model,
# #         "search_feasibility",
# #         "instance",
# #     )

# #     if search_feasibility not in {"instance", "population"}:
# #         raise ValueError(
# #             "search_feasibility must be either "
# #             "'instance' or 'population'."
# #         )

# #     random_state = int(
# #         getattr(model, "random_state", 42)
# #     )

# #     K_cce = int(model.K_cce)

# #     if K_cce <= 0:
# #         raise ValueError("model.K_cce must be a positive integer.")

# #     if x_obs.size != anm.p:
# #         raise ValueError(
# #             f"x_obs must contain {anm.p} features; "
# #             f"got {x_obs.size}."
# #         )

# #     if not np.all(np.isfinite(x_obs)):
# #         raise ValueError("x_obs must contain only finite values.")

# #     if not np.all(np.isfinite(sigma)):
# #         raise ValueError("model.sigma_ must contain only finite values.")

# #     if np.any(sigma <= 0):
# #         raise ValueError("model.sigma_ must contain positive values.")

# #     # ------------------------------------------------------------
# #     # 1. Observed point in ANM noise space
# #     # ------------------------------------------------------------

# #     u_obs = anm.inverse(x_obs)

# #     # ------------------------------------------------------------
# #     # 2. Fixed noise for population interventional expectation
# #     # ------------------------------------------------------------

# #     rng_noise = np.random.default_rng(random_state)

# #     fixed_noise = {}

# #     for j in anm.order:
# #         loc, scale = anm.noise[j]

# #         fixed_noise[j] = rng_noise.laplace(
# #             loc=loc,
# #             scale=scale,
# #             size=K_cce,
# #         )

# #     # ------------------------------------------------------------
# #     # 3. Black-box prediction helper
# #     # ------------------------------------------------------------

# #     def eval_f(x):
# #         x = np.asarray(x, dtype=float)

# #         x_2d = (
# #             x.reshape(1, -1)
# #             if x.ndim == 1
# #             else x
# #         )

# #         preds = np.asarray(model._f(x_2d))

# #         if preds.ndim == 2:
# #             if preds.shape[1] < 2:
# #                 return float(preds[0, 0])

# #             return (
# #                 float(preds[0, 1])
# #                 if len(preds) == 1
# #                 else preds[:, 1].astype(float)
# #             )

# #         preds = preds.reshape(-1)

# #         return (
# #             float(preds[0])
# #             if len(preds) == 1
# #             else preds.astype(float)
# #         )

# #     # ------------------------------------------------------------
# #     # 4. Factual prediction
# #     # ------------------------------------------------------------

# #     y_fact = float(eval_f(x_obs))

# #     # ------------------------------------------------------------
# #     # 5. Non-actionable features
# #     #
# #     # These are excluded only from direct intervention candidates.
# #     # They remain available to CAI and may still change downstream.
# #     # ------------------------------------------------------------

# #     if non_actionable is None:
# #         non_actionable = []

# #     non_actionable_idx = []

# #     for feature in non_actionable:
# #         if isinstance(feature, str):
# #             if model.feature_names is None:
# #                 raise ValueError(
# #                     "String non_actionable features require "
# #                     "model.feature_names."
# #                 )

# #             try:
# #                 idx = model.feature_names.index(feature)
# #             except ValueError as exc:
# #                 raise ValueError(
# #                     f"Unknown non_actionable feature: {feature}"
# #                 ) from exc

# #             non_actionable_idx.append(idx)

# #         else:
# #             idx = int(feature)

# #             if idx < 0 or idx >= anm.p:
# #                 raise ValueError(
# #                     f"non_actionable feature index {idx} "
# #                     f"is outside the valid range 0..{anm.p - 1}."
# #                 )

# #             non_actionable_idx.append(idx)

# #     non_actionable_idx = sorted(set(non_actionable_idx))

# #     # ------------------------------------------------------------
# #     # 6. Interventional prediction
# #     #
# #     # Population Oracle A:
# #     #
# #     #     E[f(X) | do(X_S = x_S)]
# #     #
# #     # The same deterministic fixed exogenous noise is reused for
# #     # every candidate so the search is stable and comparable.
# #     # ------------------------------------------------------------

# #     def f_int(xp, intervention_idx):
# #         xp = np.asarray(xp, dtype=float).reshape(-1)

# #         intervention_idx = np.asarray(
# #             intervention_idx,
# #             dtype=int,
# #         ).reshape(-1)

# #         S = {
# #             int(j): float(xp[j])
# #             for j in intervention_idx
# #         }

# #         samp = np.zeros(
# #             (K_cce, anm.p),
# #             dtype=float,
# #         )

# #         intervened = set(S.keys())

# #         for j in anm.order:

# #             if j in intervened:
# #                 samp[:, j] = S[j]
# #                 continue

# #             eq = anm.eqs[j]

# #             if eq.is_root:
# #                 g = np.zeros(K_cce)
# #             else:
# #                 g = eq.predict(
# #                     samp[:, eq.parents]
# #                 )

# #             samp[:, j] = (
# #                 g + fixed_noise[j]
# #             )

# #         preds = np.asarray(model._f(samp))

# #         if preds.ndim == 2:
# #             return float(
# #                 preds[:, 1].mean()
# #             )

# #         return float(
# #             preds.reshape(-1).mean()
# #         )

# #     # ------------------------------------------------------------
# #     # 7. Factual zero-change solution
# #     # ------------------------------------------------------------

# #     if y_fact >= target_prob:

# #         if verbose:
# #             print(
# #                 "  Factual instance already meets target "
# #                 "probability; returning zero-change solution."
# #             )

# #         y_baseline = f_int(
# #             x_obs,
# #             [],
# #         )

# #         return CCEResult(
# #             x_obs=x_obs,
# #             x_star=x_obs.copy(),
# #             u_obs=u_obs,
# #             u_star=u_obs.copy(),
# #             y_fact=y_fact,
# #             y_foil=y_foil,
# #             y_achieved=y_fact,
# #             violation=anm.violation(x_obs),
# #             d_causal=0.0,
# #             sparsity=1.0,
# #             changed=[],
# #             direct_interventions=[],
# #             runtime=time.time() - t0,
# #             feasible=True,
# #             search_feasible=True,
# #             target_reached=True,
# #             boundary_crossed=bool(
# #                 y_fact >= 0.50
# #             ),
# #             y_interventional=None,
# #             y_baseline_expectation=y_baseline,
# #             target_prob=target_prob,
# #             search_feasibility=search_feasibility,
# #         )

# #     # ------------------------------------------------------------
# #     # 8. CAI-guided intervention ranking
# #     # ------------------------------------------------------------

# #     cai_result = attribute_cai(
# #         model,
# #         x_obs,
# #         feature_names=model.feature_names,
# #         verbose=False,
# #     )

# #     cai = np.asarray(
# #         cai_result.cai,
# #         dtype=float,
# #     )

# #     top_idx = [
# #         int(i)
# #         for i in np.argsort(np.abs(cai))[::-1]
# #         if int(i) not in non_actionable_idx
# #     ][: int(model.top_k)]

# #     if verbose:
# #         print("\nOptimizing only:")
# #         print(
# #             "  "
# #             + "  ".join(
# #                 f"X{j + 1}"
# #                 for j in top_idx
# #             )
# #         )

# #     # ------------------------------------------------------------
# #     # 9. Causal/proximity distance
# #     # ------------------------------------------------------------

# #     def causal_distance(u_candidate):
# #         x_candidate = anm.forward(
# #             u_candidate
# #         )

# #         prox = float(
# #             np.sum(
# #                 np.abs(
# #                     x_obs - x_candidate
# #                 )
# #                 / (sigma + 1e-8)
# #             )
# #         )

# #         caus = float(
# #             model.lambda_
# #             * np.sum(
# #                 (
# #                     u_candidate
# #                     - u_obs
# #                 ) ** 2
# #             )
# #         )

# #         return prox + caus

# #     # ------------------------------------------------------------
# #     # 10. Feasibility oracle
# #     #
# #     # Instance Oracle B:
# #     #     f(x*) >= target_prob
# #     #
# #     # Population Oracle A:
# #     #     E[f(X) | do(X_S=x_S)] >= target_prob
# #     # ------------------------------------------------------------

# #     def oracle_prediction(
# #         x_candidate,
# #         intervention_idx,
# #     ):
# #         if search_feasibility == "instance":
# #             return float(
# #                 eval_f(x_candidate)
# #             )

# #         return float(
# #             f_int(
# #                 x_candidate,
# #                 intervention_idx,
# #             )
# #         )

# #     def target_reached(prediction):
# #         return bool(
# #             prediction >= target_prob
# #         )

# #     # ------------------------------------------------------------
# #     # 11. Minimal intervention search
# #     #
# #     # Verified notebook:
# #     # - 1-D ray search
# #     # - both directions
# #     # - coarse search over [0.05, 3.0]
# #     # - 25-step bisection
# #     # ------------------------------------------------------------

# #     def find_minimal_intervention(
# #         active_idx,
# #     ):
# #         u_base = u_obs.copy()

# #         x_base = anm.forward(
# #             u_base
# #         )

# #         base_pred = oracle_prediction(
# #             x_base,
# #             active_idx,
# #         )

# #         if target_reached(base_pred):
# #             return (
# #                 u_base.copy(),
# #                 base_pred,
# #             )

# #         max_step = 3.0
# #         n_steps = 30

# #         best_solution = None
# #         best_distance = np.inf
# #         best_prediction = base_pred

# #         for direction in (
# #             1.0,
# #             -1.0,
# #         ):

# #             low = 0.0
# #             high = max_step
# #             found = False

# #             # ----------------------------------------------------
# #             # Coarse ray search
# #             # ----------------------------------------------------

# #             for step in np.linspace(
# #                 0.05,
# #                 max_step,
# #                 n_steps,
# #             ):

# #                 u_test = u_obs.copy()

# #                 u_test[active_idx] = (
# #                     u_obs[active_idx]
# #                     + direction * step
# #                 )

# #                 x_test = anm.forward(
# #                     u_test
# #                 )

# #                 pred_test = oracle_prediction(
# #                     x_test,
# #                     active_idx,
# #                 )

# #                 if target_reached(
# #                     pred_test
# #                 ):
# #                     high = step
# #                     found = True
# #                     break

# #                 low = step

# #             if not found:
# #                 continue

# #             # ----------------------------------------------------
# #             # Binary refinement
# #             # ----------------------------------------------------

# #             for _ in range(25):

# #                 mid = (
# #                     low + high
# #                 ) / 2.0

# #                 u_test = u_obs.copy()

# #                 u_test[active_idx] = (
# #                     u_obs[active_idx]
# #                     + direction * mid
# #                 )

# #                 x_test = anm.forward(
# #                     u_test
# #                 )

# #                 pred_test = oracle_prediction(
# #                     x_test,
# #                     active_idx,
# #                 )

# #                 if target_reached(
# #                     pred_test
# #                 ):
# #                     high = mid
# #                 else:
# #                     low = mid

# #             # ----------------------------------------------------
# #             # Final candidate for this ray
# #             # ----------------------------------------------------

# #             u_candidate = u_obs.copy()

# #             u_candidate[active_idx] = (
# #                 u_obs[active_idx]
# #                 + direction * high
# #             )

# #             x_candidate = anm.forward(
# #                 u_candidate
# #             )

# #             pred_candidate = oracle_prediction(
# #                 x_candidate,
# #                 active_idx,
# #             )

# #             distance = causal_distance(
# #                 u_candidate
# #             )

# #             if (
# #                 target_reached(
# #                     pred_candidate
# #                 )
# #                 and distance < best_distance
# #             ):
# #                 best_solution = (
# #                     u_candidate.copy()
# #                 )

# #                 best_distance = (
# #                     distance
# #                 )

# #                 best_prediction = (
# #                     pred_candidate
# #                 )

# #         return (
# #             best_solution,
# #             best_prediction,
# #         )

# #     # ------------------------------------------------------------
# #     # 12. Progressive sparse search
# #     #
# #     # Search k = 1, 2, ..., top_k and stop at the first feasible
# #     # intervention set. This preserves the notebook's sparsity rule.
# #     # ------------------------------------------------------------

# #     best_u = None
# #     best_loss = np.inf
# #     best_pred = y_fact
# #     best_k = None
# #     best_intervention_idx = None

# #     if verbose:
# #         print(
# #             "\n[CCE] Progressive sparse search..."
# #         )

# #     for k in range(
# #         1,
# #         len(top_idx) + 1,
# #     ):

# #         active_idx = np.asarray(
# #             top_idx[:k],
# #             dtype=int,
# #         )

# #         if verbose:
# #             print(
# #                 f"\n  Trying {k} intervention "
# #                 f"variable(s): "
# #                 + " ".join(
# #                     f"X{j + 1}"
# #                     for j in active_idx
# #                 )
# #             )

# #         (
# #             u_candidate,
# #             pred_candidate,
# #         ) = find_minimal_intervention(
# #             active_idx
# #         )

# #         if u_candidate is None:

# #             if verbose:
# #                 print(
# #                     "    No feasible solution"
# #                 )

# #             continue

# #         x_candidate = anm.forward(
# #             u_candidate
# #         )

# #         pred_candidate = oracle_prediction(
# #             x_candidate,
# #             active_idx,
# #         )

# #         candidate_distance = (
# #             causal_distance(
# #                 u_candidate
# #             )
# #         )

# #         feasible = target_reached(
# #             pred_candidate
# #         )

# #         if verbose:
# #             print(
# #                 f"    f_search={pred_candidate:.3f} "
# #                 f"distance={candidate_distance:.4f} "
# #                 f"feasible={feasible}"
# #             )

# #         if feasible:

# #             best_u = (
# #                 u_candidate.copy()
# #             )

# #             best_loss = (
# #                 candidate_distance
# #             )

# #             best_pred = (
# #                 pred_candidate
# #             )

# #             best_k = k

# #             best_intervention_idx = (
# #                 active_idx.copy()
# #             )

# #             # Stop as soon as the sparsest feasible
# #             # intervention set is found.
# #             if verbose:
# #                 print(
# #                     f"\n[CCE] Sparse solution found "
# #                     f"with {best_k} "
# #                     f"intervention variable(s)."
# #                 )

# #             break

# #     # ------------------------------------------------------------
# #     # 13. No feasible counterfactual
# #     # ------------------------------------------------------------

# #     if best_u is None:

# #         if verbose:
# #             print(
# #                 "\n[CCE] No feasible counterfactual "
# #                 "found within selected "
# #                 "intervention variables."
# #             )

# #         best_u = u_obs.copy()

# #         x_star = anm.forward(
# #             best_u
# #         )

# #         y_ach = float(
# #             eval_f(x_star)
# #         )

# #         y_base_pop = f_int(
# #             x_star,
# #             [],
# #         )

# #         viol = anm.violation(
# #             x_star
# #         )

# #         boundary_crossed = bool(
# #             y_ach >= 0.50
# #         )

# #         target_reached_flag = bool(
# #             y_ach >= target_prob
# #         )

# #         return CCEResult(
# #             x_obs=x_obs,
# #             x_star=x_star,
# #             u_obs=u_obs,
# #             u_star=best_u,
# #             y_fact=y_fact,
# #             y_foil=y_foil,
# #             y_achieved=y_ach,
# #             violation=viol,
# #             d_causal=0.0,
# #             sparsity=1.0,
# #             changed=[],
# #             direct_interventions=[],
# #             runtime=time.time() - t0,
# #             feasible=False,
# #             search_feasible=False,
# #             target_reached=target_reached_flag,
# #             boundary_crossed=boundary_crossed,
# #             y_interventional=None,
# #             y_baseline_expectation=y_base_pop,
# #             target_prob=target_prob,
# #             search_feasibility=search_feasibility,
# #         )

# #     # ------------------------------------------------------------
# #     # 14. Final counterfactual
# #     # ------------------------------------------------------------

# #     x_star = anm.forward(
# #         best_u
# #     )

# #     # y_achieved remains the actual black-box prediction of x_star,
# #     # exactly as in the verified notebook.
# #     y_ach = float(
# #         eval_f(x_star)
# #     )

# #     # Population interventional prediction of the selected action.
# #     y_interv = f_int(
# #         x_star,
# #         best_intervention_idx,
# #     )

# #     viol = anm.violation(
# #         x_star
# #     )

# #     d_causal = causal_distance(
# #         best_u
# #     )

# #     # ------------------------------------------------------------
# #     # 15. Direct intervention variables
# #     # ------------------------------------------------------------

# #     intervention_vars = (
# #         best_intervention_idx.tolist()
# #         if best_intervention_idx is not None
# #         else []
# #     )

# #     direct_interventions = len(
# #         intervention_vars
# #     )

# #     # ------------------------------------------------------------
# #     # 16. Downstream observed changes
# #     #
# #     # Keep the existing display semantics:
# #     # changed contains observed features that changed by > 0.05
# #     # and excludes direct intervention variables.
# #     # ------------------------------------------------------------

# #     changed_observed = [
# #         j
# #         for j in range(anm.p)
# #         if (
# #             j not in intervention_vars
# #             and abs(
# #                 x_star[j]
# #                 - x_obs[j]
# #             ) > 0.05
# #         )
# #     ]

# #     # ------------------------------------------------------------
# #     # 17. Causal sparsity
# #     # ------------------------------------------------------------

# #     sparsity = (
# #         1.0
# #         - direct_interventions
# #         / anm.p
# #     )

# #     # ------------------------------------------------------------
# #     # 18. Verified notebook feasibility fields
# #     # ------------------------------------------------------------

# #     boundary_crossed = bool(
# #         y_ach >= 0.50
# #     )

# #     target_reached_flag = bool(
# #         y_ach >= target_prob
# #     )

# #     search_feasible = True

# #     if search_feasibility == "instance":
# #         actual_feasible = bool(
# #             target_reached_flag
# #         )
# #     else:
# #         actual_feasible = bool(
# #             search_feasible
# #         )

# #     # ------------------------------------------------------------
# #     # 19. Existing verbose output retained
# #     # ------------------------------------------------------------

# #     if verbose:

# #         print(
# #             "\n[CCE] Best feasible solution:"
# #         )

# #         print(
# #             f"  Prediction : "
# #             f"{y_fact:.3f} → "
# #             f"{y_ach:.3f}"
# #         )

# #         print(
# #             f"  Search oracle : "
# #             f"{search_feasibility}"
# #         )

# #         print(
# #             f"  Search prediction : "
# #             f"{best_pred:.4f}"
# #         )

# #         print(
# #             f"  Interventional prediction : "
# #             f"{y_interv:.4f}"
# #         )

# #         print(
# #             f"  Distance   : "
# #             f"{d_causal:.4f}"
# #         )

# #         print(
# #             f"  V_M        : "
# #             f"{viol:.4f}"
# #         )

# #         print(
# #             f"  Direct interventions : "
# #             f"{direct_interventions}"
# #         )

# #         print(
# #             f"  Downstream changes   : "
# #             f"{len(changed_observed)}"
# #         )

# #         print(
# #             f"  Causal sparsity      : "
# #             f"{sparsity:.2f}"
# #         )

# #     # ------------------------------------------------------------
# #     # 20. Return CCEResult
# #     # ------------------------------------------------------------

# #     return CCEResult(
# #         x_obs=x_obs,
# #         x_star=x_star,
# #         u_obs=u_obs,
# #         u_star=best_u,
# #         y_fact=y_fact,
# #         y_foil=y_foil,
# #         y_achieved=y_ach,
# #         violation=viol,
# #         d_causal=d_causal,
# #         sparsity=sparsity,
# #         changed=changed_observed,
# #         direct_interventions=intervention_vars,
# #         runtime=time.time() - t0,
# #         feasible=actual_feasible,
# #         search_feasible=search_feasible,
# #         target_reached=target_reached_flag,
# #         boundary_crossed=boundary_crossed,
# #         y_interventional=y_interv,
# #         y_baseline_expectation=None,
# #         target_prob=target_prob,
# #         search_feasibility=search_feasibility,
# #     )


# # __all__ = ["counterfactual_search"]

# """CCE numerical search extracted from the verified notebook."""

# import time
# import numpy as np

# from .config import TARGET_PROB
# from .results import CCEResult


# def counterfactual_search(
#     model,
#     x_obs,
#     y_foil=1.0,
#     verbose=False,
# ):
#     """Verified CCE-ANM counterfactual search."""
#     t0 = time.time()

#     anm = model.anm_
#     sigma = model.sigma_
#     target_prob = model.target_prob

#     x_obs = np.asarray(
#         x_obs,
#         dtype=float,
#     ).reshape(-1)

#     u_obs = anm.inverse(x_obs)

#     rng_noise = np.random.default_rng(
#         model.random_state
#     )

#     fixed_noise = {}

#     for j in anm.order:
#         loc, scale = anm.noise[j]
#         fixed_noise[j] = rng_noise.laplace(
#             loc=loc,
#             scale=scale,
#             size=model.K_cce,
#         )

#     def f_int(xp, intervention_idx):
#         S = {
#             int(j): float(xp[j])
#             for j in intervention_idx
#         }

#         samp = np.zeros(
#             (model.K_cce, anm.p),
#             dtype=float,
#         )

#         intervened = set(S.keys())

#         for j in anm.order:
#             if j in intervened:
#                 samp[:, j] = S[j]
#             else:
#                 eq = anm.eqs[j]

#                 g = (
#                     eq.predict(
#                         samp[:, eq.parents]
#                     )
#                     if not eq.is_root
#                     else np.zeros(
#                         model.K_cce
#                     )
#                 )

#                 samp[:, j] = (
#                     g + fixed_noise[j]
#                 )

#         preds = model._f(samp)

#         return float(
#             (
#                 preds[:, 1]
#                 if preds.ndim == 2
#                 else preds
#             ).mean()
#         )

#     y_fact = model._eval_f(x_obs)

#     if y_fact >= target_prob:
#         if verbose:
#             print(
#                 "  Factual instance already meets "
#                 "target probability; returning "
#                 "zero-change solution."
#             )

#         return CCEResult(
#             x_obs=x_obs,
#             x_star=x_obs.copy(),
#             u_obs=u_obs,
#             u_star=u_obs.copy(),
#             y_fact=y_fact,
#             y_foil=y_foil,
#             y_achieved=y_fact,
#             violation=anm.violation(x_obs),
#             d_causal=0.0,
#             sparsity=1.0,
#             changed=[],
#             direct_interventions=[],
#             runtime=time.time() - t0,
#             feasible=True,
#             search_feasible=True,
#             target_reached=True,
#             boundary_crossed=bool(
#                 y_fact >= 0.50
#             ),
#             y_interventional=None,
#             y_baseline_expectation=f_int(
#                 x_obs,
#                 [],
#             ),
#             target_prob=target_prob,
#             search_feasibility=(
#                 model.search_feasibility
#             ),
#         )

#     cai = model.attribute(
#         x_obs,
#         verbose=False,
#     ).cai

#     top_idx = np.argsort(
#         np.abs(cai)
#     )[::-1][:model.top_k]

#     def causal_distance(u_candidate):
#         x_candidate = anm.forward(
#             u_candidate
#         )

#         proximity = float(
#             np.sum(
#                 np.abs(
#                     x_obs - x_candidate
#                 ) / sigma
#             )
#         )

#         causal = float(
#             model.lambda_
#             * np.sum(
#                 (u_candidate - u_obs) ** 2
#             )
#         )

#         return proximity + causal

#     def find_minimal_intervention(
#         active_idx
#     ):
#         u_base = u_obs.copy()
#         x_base = anm.forward(u_base)

#         if model.search_feasibility == "instance":
#             base_pred = model._eval_f(
#                 x_base
#             )
#         else:
#             base_pred = f_int(
#                 x_base,
#                 active_idx,
#             )

#         if base_pred >= target_prob:
#             return u_base.copy(), base_pred

#         max_step = 3.0
#         n_steps = 30

#         best_solution = None
#         best_distance = np.inf
#         best_prediction = base_pred

#         for direction in [
#             1.0,
#             -1.0,
#         ]:
#             low = 0.0
#             high = max_step
#             found = False

#             for step in np.linspace(
#                 0.05,
#                 max_step,
#                 n_steps,
#             ):
#                 u_test = u_obs.copy()

#                 u_test[active_idx] = (
#                     u_obs[active_idx]
#                     + direction * step
#                 )

#                 x_test = anm.forward(
#                     u_test
#                 )

#                 if (
#                     model.search_feasibility
#                     == "instance"
#                 ):
#                     pred_test = model._eval_f(
#                         x_test
#                     )
#                 else:
#                     pred_test = f_int(
#                         x_test,
#                         active_idx,
#                     )

#                 if pred_test >= target_prob:
#                     high = step
#                     found = True
#                     break

#                 low = step

#             if not found:
#                 continue

#             for _ in range(25):
#                 mid = (
#                     low + high
#                 ) / 2.0

#                 u_test = u_obs.copy()

#                 u_test[active_idx] = (
#                     u_obs[active_idx]
#                     + direction * mid
#                 )

#                 x_test = anm.forward(
#                     u_test
#                 )

#                 if (
#                     model.search_feasibility
#                     == "instance"
#                 ):
#                     pred_test = model._eval_f(
#                         x_test
#                     )
#                 else:
#                     pred_test = f_int(
#                         x_test,
#                         active_idx,
#                     )

#                 if pred_test >= target_prob:
#                     high = mid
#                 else:
#                     low = mid

#             u_candidate = u_obs.copy()

#             u_candidate[active_idx] = (
#                 u_obs[active_idx]
#                 + direction * high
#             )

#             x_candidate = anm.forward(
#                 u_candidate
#             )

#             if (
#                 model.search_feasibility
#                 == "instance"
#             ):
#                 pred_candidate = model._eval_f(
#                     x_candidate
#                 )
#             else:
#                 pred_candidate = f_int(
#                     x_candidate,
#                     active_idx,
#                 )

#             distance = causal_distance(
#                 u_candidate
#             )

#             if (
#                 pred_candidate >= target_prob
#                 and distance < best_distance
#             ):
#                 best_solution = (
#                     u_candidate.copy()
#                 )
#                 best_distance = distance
#                 best_prediction = (
#                     pred_candidate
#                 )

#         return (
#             best_solution,
#             best_prediction,
#         )

#     best_u = None
#     best_loss = np.inf
#     best_pred = y_fact
#     best_k = None
#     best_intervention_idx = None

#     for k in range(
#         1,
#         len(top_idx) + 1,
#     ):
#         active_idx = top_idx[:k]

#         u_candidate, pred_candidate = (
#             find_minimal_intervention(
#                 active_idx
#             )
#         )

#         if u_candidate is None:
#             continue

#         x_candidate = anm.forward(
#             u_candidate
#         )

#         if model.search_feasibility == "instance":
#             pred_candidate = model._eval_f(
#                 x_candidate
#             )
#         else:
#             pred_candidate = f_int(
#                 x_candidate,
#                 active_idx,
#             )

#         candidate_distance = (
#             causal_distance(
#                 u_candidate
#             )
#         )

#         feasible = (
#             pred_candidate >= target_prob
#         )

#         if feasible:
#             best_u = u_candidate.copy()
#             best_loss = candidate_distance
#             best_pred = pred_candidate
#             best_k = k
#             best_intervention_idx = (
#                 active_idx.copy()
#             )
#             break

#     if best_u is None:
#         best_u = u_obs.copy()
#         x_star = anm.forward(best_u)

#         y_ach = model._eval_f(x_star)

#         y_base_pop = f_int(
#             x_star,
#             [],
#         )

#         violation = anm.violation(
#             x_star
#         )

#         return CCEResult(
#             x_obs=x_obs,
#             x_star=x_star,
#             u_obs=u_obs,
#             u_star=best_u,
#             y_fact=y_fact,
#             y_foil=y_foil,
#             y_achieved=y_ach,
#             violation=violation,
#             d_causal=0.0,
#             sparsity=1.0,
#             changed=[],
#             direct_interventions=[],
#             runtime=time.time() - t0,
#             feasible=False,
#             search_feasible=False,
#             target_reached=bool(
#                 y_ach >= target_prob
#             ),
#             boundary_crossed=bool(
#                 y_ach >= 0.50
#             ),
#             y_interventional=None,
#             y_baseline_expectation=y_base_pop,
#             target_prob=target_prob,
#             search_feasibility=(
#                 model.search_feasibility
#             ),
#         )

#     x_star = anm.forward(best_u)

#     y_ach = model._eval_f(x_star)

#     y_interventional = f_int(
#         x_star,
#         best_intervention_idx,
#     )

#     violation = anm.violation(
#         x_star
#     )

#     d_causal = causal_distance(
#         best_u
#     )

#     changed_observed = [
#         j
#         for j in range(anm.p)
#         if abs(
#             x_star[j] - x_obs[j]
#         ) > 0.05
#     ]

#     intervention_vars = (
#         best_intervention_idx.tolist()
#         if best_intervention_idx is not None
#         else []
#     )

#     direct_interventions = len(
#         intervention_vars
#     )

#     sparsity = (
#         1.0
#         - direct_interventions / anm.p
#     )

#     boundary_crossed = bool(
#         y_ach >= 0.50
#     )

#     target_reached = bool(
#         y_ach >= target_prob
#     )

#     search_feasible = True

#     actual_feasible = bool(
#         target_reached
#         if model.search_feasibility
#         == "instance"
#         else search_feasible
#     )

#     return CCEResult(
#         x_obs=x_obs,
#         x_star=x_star,
#         u_obs=u_obs,
#         u_star=best_u,
#         y_fact=y_fact,
#         y_foil=y_foil,
#         y_achieved=y_ach,
#         violation=violation,
#         d_causal=d_causal,
#         sparsity=sparsity,
#         changed=changed_observed,
#         direct_interventions=intervention_vars,
#         runtime=time.time() - t0,
#         feasible=actual_feasible,
#         search_feasible=search_feasible,
#         target_reached=target_reached,
#         boundary_crossed=boundary_crossed,
#         y_interventional=y_interventional,
#         y_baseline_expectation=None,
#         target_prob=target_prob,
#         search_feasibility=(
#             model.search_feasibility
#         ),
#     )


# __all__ = [
#     "counterfactual_search",
# ]


import time

import numpy as np

from .config import TARGET_PROB
from .results import CCEResult
from .cai import attribute_cai


def counterfactual_search(
    model,
    x_obs,
    y_foil,
    non_actionable=None,
    verbose=False,
):
    """
    Search for a causal counterfactual using the verified CCE-ANM
    counterfactual algorithm.

    The search follows the verified notebook:

    1. Map the observation to ANM noise space.
    2. Evaluate the factual black-box probability.
    3. Rank intervention candidates using CAI.
    4. Use a deterministic fixed-noise population simulator.
    5. Support two feasibility oracles:
       - instance:      f(x*) >= target_prob
       - population:    E[f(X) | do(X_S=x_S)] >= target_prob
    6. Search progressively over the top-k causal variables.
    7. For each active intervention set, search both directions using
       a coarse 1-D ray search followed by bisection.
    8. Return the sparsest feasible intervention set.

    The existing CCE result fields used by the display layer are retained:
    x_obs, x_star, u_obs, u_star, y_fact, y_foil, y_achieved,
    violation, d_causal, sparsity, changed, direct_interventions,
    runtime, and feasible.

    Additional result fields introduced by the verified notebook are:
    search_feasible, target_reached, boundary_crossed,
    y_interventional, y_baseline_expectation, target_prob,
    and search_feasibility.
    """

    t0 = time.time()

    x_obs = np.asarray(x_obs, dtype=float).reshape(-1)

    anm = model.anm_
    sigma = np.asarray(model.sigma_, dtype=float)

    target_prob = float(
        getattr(model, "target_prob", TARGET_PROB)
    )

    search_feasibility = getattr(
        model,
        "search_feasibility",
        "instance",
    )

    if search_feasibility not in {"instance", "population"}:
        raise ValueError(
            "search_feasibility must be either "
            "'instance' or 'population'."
        )

    random_state = int(
        getattr(model, "random_state", 42)
    )

    K_cce = int(model.K_cce)

    if K_cce <= 0:
        raise ValueError("model.K_cce must be a positive integer.")

    if x_obs.size != anm.p:
        raise ValueError(
            f"x_obs must contain {anm.p} features; "
            f"got {x_obs.size}."
        )

    if not np.all(np.isfinite(x_obs)):
        raise ValueError("x_obs must contain only finite values.")

    if not np.all(np.isfinite(sigma)):
        raise ValueError("model.sigma_ must contain only finite values.")

    if np.any(sigma <= 0):
        raise ValueError("model.sigma_ must contain positive values.")

    # ------------------------------------------------------------
    # 1. Observed point in ANM noise space
    # ------------------------------------------------------------

    u_obs = anm.inverse(x_obs)

    # ------------------------------------------------------------
    # 2. Fixed noise for population interventional expectation
    # ------------------------------------------------------------

    rng_noise = np.random.default_rng(random_state)

    fixed_noise = {}

    for j in anm.order:
        loc, scale = anm.noise[j]

        fixed_noise[j] = rng_noise.laplace(
            loc=loc,
            scale=scale,
            size=K_cce,
        )

    # ------------------------------------------------------------
    # 3. Black-box prediction helper
    # ------------------------------------------------------------

    def eval_f(x):
        x = np.asarray(x, dtype=float)

        x_2d = (
            x.reshape(1, -1)
            if x.ndim == 1
            else x
        )

        preds = np.asarray(model._f(x_2d))

        if preds.ndim == 2:
            if preds.shape[1] < 2:
                return float(preds[0, 0])

            return (
                float(preds[0, 1])
                if len(preds) == 1
                else preds[:, 1].astype(float)
            )

        preds = preds.reshape(-1)

        return (
            float(preds[0])
            if len(preds) == 1
            else preds.astype(float)
        )

    # ------------------------------------------------------------
    # 4. Factual prediction
    # ------------------------------------------------------------

    y_fact = float(eval_f(x_obs))

    # ------------------------------------------------------------
    # 5. Non-actionable features
    #
    # These are excluded only from direct intervention candidates.
    # They remain available to CAI and may still change downstream.
    # ------------------------------------------------------------

    if non_actionable is None:
        non_actionable = []

    non_actionable_idx = []

    for feature in non_actionable:
        if isinstance(feature, str):
            if model.feature_names is None:
                raise ValueError(
                    "String non_actionable features require "
                    "model.feature_names."
                )

            try:
                idx = model.feature_names.index(feature)
            except ValueError as exc:
                raise ValueError(
                    f"Unknown non_actionable feature: {feature}"
                ) from exc

            non_actionable_idx.append(idx)

        else:
            idx = int(feature)

            if idx < 0 or idx >= anm.p:
                raise ValueError(
                    f"non_actionable feature index {idx} "
                    f"is outside the valid range 0..{anm.p - 1}."
                )

            non_actionable_idx.append(idx)

    non_actionable_idx = sorted(set(non_actionable_idx))

    # ------------------------------------------------------------
    # 6. Interventional prediction
    #
    # Population Oracle A:
    #
    #     E[f(X) | do(X_S = x_S)]
    #
    # The same deterministic fixed exogenous noise is reused for
    # every candidate so the search is stable and comparable.
    # ------------------------------------------------------------

    def f_int(xp, intervention_idx):
        xp = np.asarray(xp, dtype=float).reshape(-1)

        intervention_idx = np.asarray(
            intervention_idx,
            dtype=int,
        ).reshape(-1)

        S = {
            int(j): float(xp[j])
            for j in intervention_idx
        }

        samp = np.zeros(
            (K_cce, anm.p),
            dtype=float,
        )

        intervened = set(S.keys())

        for j in anm.order:

            if j in intervened:
                samp[:, j] = S[j]
                continue

            eq = anm.eqs[j]

            if eq.is_root:
                g = np.zeros(K_cce)
            else:
                g = eq.predict(
                    samp[:, eq.parents]
                )

            samp[:, j] = (
                g + fixed_noise[j]
            )

        preds = np.asarray(model._f(samp))

        if preds.ndim == 2:
            return float(
                preds[:, 1].mean()
            )

        return float(
            preds.reshape(-1).mean()
        )

    # ------------------------------------------------------------
    # 7. Factual zero-change solution
    # ------------------------------------------------------------

    if y_fact >= target_prob:

        if verbose:
            print(
                "  Factual instance already meets target "
                "probability; returning zero-change solution."
            )

        y_baseline = f_int(
            x_obs,
            [],
        )

        return CCEResult(
            x_obs=x_obs,
            x_star=x_obs.copy(),
            u_obs=u_obs,
            u_star=u_obs.copy(),
            y_fact=y_fact,
            y_foil=y_foil,
            y_achieved=y_fact,
            violation=anm.violation(x_obs),
            d_causal=0.0,
            sparsity=1.0,
            changed=[],
            direct_interventions=[],
            runtime=time.time() - t0,
            feasible=True,
            search_feasible=True,
            target_reached=True,
            boundary_crossed=bool(
                y_fact >= 0.50
            ),
            y_interventional=None,
            y_baseline_expectation=y_baseline,
            target_prob=target_prob,
            search_feasibility=search_feasibility,
        )

    # ------------------------------------------------------------
    # 8. CAI-guided intervention ranking
    # ------------------------------------------------------------

    cai_result = attribute_cai(
        model,
        x_obs,
        feature_names=model.feature_names,
        verbose=False,
    )

    cai = np.asarray(
        cai_result.cai,
        dtype=float,
    )

    top_idx = [
        int(i)
        for i in np.argsort(np.abs(cai))[::-1]
        if int(i) not in non_actionable_idx
    ][: int(model.top_k)]

    if verbose:
        print("\nOptimizing only:")
        print(
            "  "
            + "  ".join(
                f"X{j + 1}"
                for j in top_idx
            )
        )

    # ------------------------------------------------------------
    # 9. Causal/proximity distance
    # ------------------------------------------------------------

    def causal_distance(u_candidate):
        x_candidate = anm.forward(
            u_candidate
        )

        prox = float(
            np.sum(
                np.abs(
                    x_obs - x_candidate
                )
                / (sigma + 1e-8)
            )
        )

        caus = float(
            model.lambda_
            * np.sum(
                (
                    u_candidate
                    - u_obs
                ) ** 2
            )
        )

        return prox + caus

    # ------------------------------------------------------------
    # 10. Feasibility oracle
    #
    # Instance Oracle B:
    #     f(x*) >= target_prob
    #
    # Population Oracle A:
    #     E[f(X) | do(X_S=x_S)] >= target_prob
    # ------------------------------------------------------------

    def oracle_prediction(
        x_candidate,
        intervention_idx,
    ):
        if search_feasibility == "instance":
            return float(
                eval_f(x_candidate)
            )

        return float(
            f_int(
                x_candidate,
                intervention_idx,
            )
        )

    def target_reached(prediction):
        return bool(
            prediction >= target_prob
        )

    # ------------------------------------------------------------
    # 11. Minimal intervention search
    #
    # Verified notebook:
    # - 1-D ray search
    # - both directions
    # - coarse search over [0.05, 3.0]
    # - 25-step bisection
    # ------------------------------------------------------------

    def find_minimal_intervention(
        active_idx,
    ):
        u_base = u_obs.copy()

        x_base = anm.forward(
            u_base
        )

        base_pred = oracle_prediction(
            x_base,
            active_idx,
        )

        if target_reached(base_pred):
            return (
                u_base.copy(),
                base_pred,
            )

        max_step = 3.0
        n_steps = 30

        best_solution = None
        best_distance = np.inf
        best_prediction = base_pred

        for direction in (
            1.0,
            -1.0,
        ):

            low = 0.0
            high = max_step
            found = False

            # ----------------------------------------------------
            # Coarse ray search
            # ----------------------------------------------------

            for step in np.linspace(
                0.05,
                max_step,
                n_steps,
            ):

                u_test = u_obs.copy()

                u_test[active_idx] = (
                    u_obs[active_idx]
                    + direction * step
                )

                x_test = anm.forward(
                    u_test
                )

                pred_test = oracle_prediction(
                    x_test,
                    active_idx,
                )

                if target_reached(
                    pred_test
                ):
                    high = step
                    found = True
                    break

                low = step

            if not found:
                continue

            # ----------------------------------------------------
            # Binary refinement
            # ----------------------------------------------------

            for _ in range(25):

                mid = (
                    low + high
                ) / 2.0

                u_test = u_obs.copy()

                u_test[active_idx] = (
                    u_obs[active_idx]
                    + direction * mid
                )

                x_test = anm.forward(
                    u_test
                )

                pred_test = oracle_prediction(
                    x_test,
                    active_idx,
                )

                if target_reached(
                    pred_test
                ):
                    high = mid
                else:
                    low = mid

            # ----------------------------------------------------
            # Final candidate for this ray
            # ----------------------------------------------------

            u_candidate = u_obs.copy()

            u_candidate[active_idx] = (
                u_obs[active_idx]
                + direction * high
            )

            x_candidate = anm.forward(
                u_candidate
            )

            pred_candidate = oracle_prediction(
                x_candidate,
                active_idx,
            )

            distance = causal_distance(
                u_candidate
            )

            if (
                target_reached(
                    pred_candidate
                )
                and distance < best_distance
            ):
                best_solution = (
                    u_candidate.copy()
                )

                best_distance = (
                    distance
                )

                best_prediction = (
                    pred_candidate
                )

        return (
            best_solution,
            best_prediction,
        )

    # ------------------------------------------------------------
    # 12. Progressive sparse search
    #
    # Search k = 1, 2, ..., top_k and stop at the first feasible
    # intervention set. This preserves the notebook's sparsity rule.
    # ------------------------------------------------------------

    best_u = None
    best_loss = np.inf
    best_pred = y_fact
    best_k = None
    best_intervention_idx = None

    if verbose:
        print(
            "\n[CCE] Progressive sparse search..."
        )

    for k in range(
        1,
        len(top_idx) + 1,
    ):

        active_idx = np.asarray(
            top_idx[:k],
            dtype=int,
        )

        if verbose:
            print(
                f"\n  Trying {k} intervention "
                f"variable(s): "
                + " ".join(
                    f"X{j + 1}"
                    for j in active_idx
                )
            )

        (
            u_candidate,
            pred_candidate,
        ) = find_minimal_intervention(
            active_idx
        )

        if u_candidate is None:

            if verbose:
                print(
                    "    No feasible solution"
                )

            continue

        x_candidate = anm.forward(
            u_candidate
        )

        pred_candidate = oracle_prediction(
            x_candidate,
            active_idx,
        )

        candidate_distance = (
            causal_distance(
                u_candidate
            )
        )

        feasible = target_reached(
            pred_candidate
        )

        if verbose:
            print(
                f"    f_search={pred_candidate:.3f} "
                f"distance={candidate_distance:.4f} "
                f"feasible={feasible}"
            )

        if feasible:

            best_u = (
                u_candidate.copy()
            )

            best_loss = (
                candidate_distance
            )

            best_pred = (
                pred_candidate
            )

            best_k = k

            best_intervention_idx = (
                active_idx.copy()
            )

            # Stop as soon as the sparsest feasible
            # intervention set is found.
            if verbose:
                print(
                    f"\n[CCE] Sparse solution found "
                    f"with {best_k} "
                    f"intervention variable(s)."
                )

            break

    # ------------------------------------------------------------
    # 13. No feasible counterfactual
    # ------------------------------------------------------------

    if best_u is None:

        if verbose:
            print(
                "\n[CCE] No feasible counterfactual "
                "found within selected "
                "intervention variables."
            )

        best_u = u_obs.copy()

        x_star = anm.forward(
            best_u
        )

        y_ach = float(
            eval_f(x_star)
        )

        y_base_pop = f_int(
            x_star,
            [],
        )

        viol = anm.violation(
            x_star
        )

        boundary_crossed = bool(
            y_ach >= 0.50
        )

        target_reached_flag = bool(
            y_ach >= target_prob
        )

        return CCEResult(
            x_obs=x_obs,
            x_star=x_star,
            u_obs=u_obs,
            u_star=best_u,
            y_fact=y_fact,
            y_foil=y_foil,
            y_achieved=y_ach,
            violation=viol,
            d_causal=0.0,
            sparsity=1.0,
            changed=[],
            direct_interventions=[],
            runtime=time.time() - t0,
            feasible=False,
            search_feasible=False,
            target_reached=target_reached_flag,
            boundary_crossed=boundary_crossed,
            y_interventional=None,
            y_baseline_expectation=y_base_pop,
            target_prob=target_prob,
            search_feasibility=search_feasibility,
        )

    # ------------------------------------------------------------
    # 14. Final counterfactual
    # ------------------------------------------------------------

    x_star = anm.forward(
        best_u
    )

    # y_achieved remains the actual black-box prediction of x_star,
    # exactly as in the verified notebook.
    y_ach = float(
        eval_f(x_star)
    )

    # Population interventional prediction of the selected action.
    y_interv = f_int(
        x_star,
        best_intervention_idx,
    )

    viol = anm.violation(
        x_star
    )

    d_causal = causal_distance(
        best_u
    )

    # ------------------------------------------------------------
    # 15. Direct intervention variables
    # ------------------------------------------------------------

    intervention_vars = (
        best_intervention_idx.tolist()
        if best_intervention_idx is not None
        else []
    )

    direct_interventions = len(
        intervention_vars
    )

    # ------------------------------------------------------------
    # 16. Downstream observed changes
    #
    # Keep the existing display semantics:
    # changed contains observed features that changed by > 0.05
    # and excludes direct intervention variables.
    # ------------------------------------------------------------

    changed_observed = [
        j
        for j in range(anm.p)
        if (
            j not in intervention_vars
            and abs(
                x_star[j]
                - x_obs[j]
            ) > 0.05
        )
    ]

    # ------------------------------------------------------------
    # 17. Causal sparsity
    # ------------------------------------------------------------

    sparsity = (
        1.0
        - direct_interventions
        / anm.p
    )

    # ------------------------------------------------------------
    # 18. Verified notebook feasibility fields
    # ------------------------------------------------------------

    boundary_crossed = bool(
        y_ach >= 0.50
    )

    target_reached_flag = bool(
        y_ach >= target_prob
    )

    search_feasible = True

    if search_feasibility == "instance":
        actual_feasible = bool(
            target_reached_flag
        )
    else:
        actual_feasible = bool(
            search_feasible
        )

    # ------------------------------------------------------------
    # 19. Existing verbose output retained
    # ------------------------------------------------------------

    if verbose:

        print(
            "\n[CCE] Best feasible solution:"
        )

        print(
            f"  Prediction : "
            f"{y_fact:.3f} → "
            f"{y_ach:.3f}"
        )

        print(
            f"  Search oracle : "
            f"{search_feasibility}"
        )

        print(
            f"  Search prediction : "
            f"{best_pred:.4f}"
        )

        print(
            f"  Interventional prediction : "
            f"{y_interv:.4f}"
        )

        print(
            f"  Distance   : "
            f"{d_causal:.4f}"
        )

        print(
            f"  V_M        : "
            f"{viol:.4f}"
        )

        print(
            f"  Direct interventions : "
            f"{direct_interventions}"
        )

        print(
            f"  Downstream changes   : "
            f"{len(changed_observed)}"
        )

        print(
            f"  Causal sparsity      : "
            f"{sparsity:.2f}"
        )

    # ------------------------------------------------------------
    # 20. Return CCEResult
    # ------------------------------------------------------------

    return CCEResult(
        x_obs=x_obs,
        x_star=x_star,
        u_obs=u_obs,
        u_star=best_u,
        y_fact=y_fact,
        y_foil=y_foil,
        y_achieved=y_ach,
        violation=viol,
        d_causal=d_causal,
        sparsity=sparsity,
        changed=changed_observed,
        direct_interventions=intervention_vars,
        runtime=time.time() - t0,
        feasible=actual_feasible,
        search_feasible=search_feasible,
        target_reached=target_reached_flag,
        boundary_crossed=boundary_crossed,
        y_interventional=y_interv,
        y_baseline_expectation=None,
        target_prob=target_prob,
        search_feasibility=search_feasibility,
    )


__all__ = ["counterfactual_search"]
