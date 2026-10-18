
# # import numpy as np

# # from .results import CAIResult


# # def attribute_cai(
# #     model,
# #     x_obs,
# #     feature_names=None,
# #     verbose=False,
# # ):
# #     """
# #     Compute CAI_j = E_M[f | do(X_j = x_j)] - E_M[f] for all features j.

# #     This is the exact CAI logic extracted from the notebook's
# #     CCE_ANM_Model.attribute() method.
# #     """

# #     anm = model.anm_

# #     def predict_samples(samp):
# #         p = model._f(samp)

# #         return np.asarray(
# #             p[:, 1] if p.ndim == 2 else p,
# #             dtype=float
# #         )

# #     if verbose:
# #         print(f"\n[CAI] K={model.K_cai}...")

# #     # -------------------------------------------------------
# #     # Baseline Monte Carlo predictions
# #     # -------------------------------------------------------

# #     baseline_predictions = predict_samples(
# #         anm.do_sample(
# #             {},
# #             K=model.K_cai
# #         )
# #     )

# #     baseline = float(
# #         np.mean(baseline_predictions)
# #     )

# #     if verbose:
# #         print(
# #             f"  Baseline E_M[f(X)] = "
# #             f"{baseline:.4f}"
# #         )

# #     # -------------------------------------------------------
# #     # Storage for CAI and uncertainty diagnostics
# #     # -------------------------------------------------------

# #     f_do = np.zeros(anm.p)

# #     standard_errors = np.zeros(anm.p)

# #     confidence_intervals = np.zeros(
# #         (anm.p, 2)
# #     )

# #     intervention_values = []

# #     # -------------------------------------------------------
# #     # Per-feature interventions
# #     # -------------------------------------------------------

# #     for j in range(anm.p):

# #         intervention_predictions = predict_samples(
# #             anm.do_sample(
# #                 {j: float(x_obs[j])},
# #                 K=model.K_cai
# #             )
# #         )

# #         intervention_values.append(
# #             intervention_predictions
# #         )

# #         intervention_mean = float(
# #             np.mean(intervention_predictions)
# #         )

# #         f_do[j] = intervention_mean

# #         # CAI
# #         cai_j = (
# #             intervention_mean
# #             - baseline
# #         )

# #         # ---------------------------------------------------
# #         # Monte Carlo standard error of the difference
# #         # ---------------------------------------------------

# #         se_j = np.sqrt(
# #             np.var(
# #                 intervention_predictions,
# #                 ddof=1
# #             ) / model.K_cai
# #             +
# #             np.var(
# #                 baseline_predictions,
# #                 ddof=1
# #             ) / model.K_cai
# #         )

# #         standard_errors[j] = float(se_j)

# #         # ---------------------------------------------------
# #         # Approximate 95% confidence interval
# #         # ---------------------------------------------------

# #         confidence_intervals[j] = (
# #             cai_j - 1.96 * se_j,
# #             cai_j + 1.96 * se_j
# #         )

# #         if verbose:
# #             print(
# #                 f"  do(X{j+1}={x_obs[j]:.3f}) "
# #                 f"→ E[f]={f_do[j]:.4f}  "
# #                 f"CAI={cai_j:+.4f}  "
# #                 f"SE={se_j:.4f}"
# #             )

# #     # -------------------------------------------------------
# #     # Final CAI
# #     # -------------------------------------------------------

# #     cai = f_do - baseline

# #     cai_norm = (
# #         cai /
# #         (np.abs(cai).sum() + 1e-8)
# #     )

# #     # -------------------------------------------------------
# #     # Return result
# #     # -------------------------------------------------------

# #     return CAIResult(
# #         x_obs=x_obs,
# #         cai=cai,
# #         cai_norm=cai_norm,
# #         baseline=baseline,
# #         f_do=f_do,
# #         feature_names=feature_names,
# #         standard_errors=standard_errors,
# #         confidence_intervals=confidence_intervals,
# #         intervention_values=intervention_values,
# #         n_samples=model.K_cai,
# #     )

# import numpy as np

# from .results import CAIResult


# def attribute_cai(
#     model,
#     x_obs,
#     feature_names=None,
#     verbose=False,
# ):
#     """
#     Compute causal average intervention (CAI) for every feature.

#     The implementation follows the verified notebook's CAI procedure:

#         CAI_j = E[f(X) | do(X_j = x_j)] - E[f(X)]

#     The baseline and every intervention use the same Monte Carlo
#     exogenous-noise draws (common random numbers). This makes the
#     feature-wise differences paired rather than independently sampled,
#     reducing Monte Carlo noise in the CAI estimate and its standard error.

#     Existing CAIResult fields are preserved so the current display layer
#     remains unchanged.
#     """

#     anm = model.anm_

#     x_obs = np.asarray(x_obs, dtype=float).reshape(-1)
#     K = int(model.K_cai)

#     if K <= 0:
#         raise ValueError("model.K_cai must be a positive integer.")

#     if x_obs.size != anm.p:
#         raise ValueError(
#             f"x_obs must contain {anm.p} features; got {x_obs.size}."
#         )

#     if not np.all(np.isfinite(x_obs)):
#         raise ValueError("x_obs must contain only finite values.")

#     # -------------------------------------------------------
#     # Black-box prediction helper
#     # -------------------------------------------------------

#     def predict_samples(samples):
#         samples = np.asarray(samples, dtype=float)
#         predictions = np.asarray(model._f(samples))

#         if predictions.ndim == 2:
#             if predictions.shape[1] < 2:
#                 return predictions[:, 0].astype(float)
#             return predictions[:, 1].astype(float)

#         return predictions.reshape(-1).astype(float)

#     if verbose:
#         print(f"\n[CAI] K={K}...")

#     # -------------------------------------------------------
#     # Common Random Numbers
#     # -------------------------------------------------------
#     # One deterministic set of exogenous-noise samples is reused for
#     # baseline and every feature intervention.
#     # -------------------------------------------------------

#     random_state = int(getattr(model, "random_state", 42))
#     rng = np.random.default_rng(random_state)

#     u_noise = {}

#     for j in anm.order:
#         loc, scale = anm.noise[j]
#         u_noise[j] = rng.laplace(
#             loc=loc,
#             scale=scale,
#             size=K,
#         )

#     # -------------------------------------------------------
#     # Baseline Monte Carlo predictions
#     # -------------------------------------------------------

#     baseline_samples = anm.do_sample(
#         {},
#         K=K,
#         u_noise=u_noise,
#     )

#     baseline_predictions = predict_samples(baseline_samples)

#     if baseline_predictions.size != K:
#         raise ValueError(
#             "Black-box prediction count does not match model.K_cai."
#         )

#     baseline = float(np.mean(baseline_predictions))

#     if verbose:
#         print(
#             f"  Baseline E_M[f(X)] = "
#             f"{baseline:.4f}"
#         )

#     # -------------------------------------------------------
#     # Storage for CAI and uncertainty diagnostics
#     # -------------------------------------------------------

#     f_do = np.zeros(anm.p, dtype=float)
#     standard_errors = np.zeros(anm.p, dtype=float)
#     confidence_intervals = np.zeros((anm.p, 2), dtype=float)
#     intervention_values = []

#     # Internal diagnostics from the notebook's CRN comparison.
#     # These do not alter the existing CAIResult/display contract.
#     unpaired_standard_errors = np.zeros(anm.p, dtype=float)
#     variance_reduction = np.zeros(anm.p, dtype=float)

#     # -------------------------------------------------------
#     # Per-feature interventions
#     # -------------------------------------------------------

#     for j in range(anm.p):

#         intervention_predictions = predict_samples(
#             anm.do_sample(
#                 {j: float(x_obs[j])},
#                 K=K,
#                 u_noise=u_noise,
#             )
#         )

#         if intervention_predictions.size != K:
#             raise ValueError(
#                 "Black-box prediction count does not match model.K_cai."
#             )

#         # intervention_values.append(intervention_predictions)
#         intervention_values.append(float(x_obs[j]))

#         intervention_mean = float(
#             np.mean(intervention_predictions)
#         )

#         f_do[j] = intervention_mean

#         # ---------------------------------------------------
#         # CAI using paired CRN samples
#         # ---------------------------------------------------

#         paired_difference = (
#             intervention_predictions
#             - baseline_predictions
#         )

#         cai_j = float(np.mean(paired_difference))

#         # Paired Monte Carlo SE: this is the uncertainty estimate used
#         # by the verified notebook after introducing CRN.
#         if K > 1:
#             paired_se = float(
#                 np.std(paired_difference, ddof=1)
#                 / np.sqrt(K)
#             )
#         else:
#             paired_se = 0.0

#         standard_errors[j] = paired_se

#         # ---------------------------------------------------
#         # 95% paired confidence interval
#         # ---------------------------------------------------

#         confidence_intervals[j] = (
#             cai_j - 1.96 * paired_se,
#             cai_j + 1.96 * paired_se,
#         )

#         # ---------------------------------------------------
#         # Unpaired diagnostic / variance reduction
#         # ---------------------------------------------------

#         if K > 1:
#             baseline_var = float(
#                 np.var(baseline_predictions, ddof=1)
#             )
#             intervention_var = float(
#                 np.var(intervention_predictions, ddof=1)
#             )

#             unpaired_var = (
#                 baseline_var / K
#                 + intervention_var / K
#             )

#             unpaired_se = float(
#                 np.sqrt(max(unpaired_var, 0.0))
#             )

#             unpaired_standard_errors[j] = unpaired_se

#             if unpaired_var > 0.0:
#                 paired_var = paired_se ** 2
#                 variance_reduction[j] = float(
#                     1.0 - paired_var / unpaired_var
#                 )
#             else:
#                 variance_reduction[j] = 0.0
#         else:
#             unpaired_standard_errors[j] = 0.0
#             variance_reduction[j] = 0.0

#         if verbose:
#             print(
#                 f"  do(X{j + 1}={x_obs[j]:.3f}) "
#                 f"→ E[f]={f_do[j]:.4f}  "
#                 f"CAI={cai_j:+.4f}  "
#                 f"SE={paired_se:.4f}"
#             )

#     # -------------------------------------------------------
#     # Final CAI
#     # -------------------------------------------------------

#     cai = f_do - baseline

#     # Keep the result exactly consistent with the paired computation.
#     # The explicit vector calculation is equivalent to the per-feature
#     # paired means above and preserves the original CAI API.
#     cai = np.asarray(cai, dtype=float)

#     cai_norm = (
#         cai /
#         (np.abs(cai).sum() + 1e-8)
#     )

#     # The notebook diagnostics are intentionally kept internal here.
#     # CAIResult and the existing display layer continue to receive the
#     # same public fields as before.
#     _ = unpaired_standard_errors
#     _ = variance_reduction

#     # -------------------------------------------------------
#     # Return result
#     # -------------------------------------------------------

#     return CAIResult(
#         x_obs=x_obs,
#         cai=cai,
#         cai_norm=cai_norm,
#         baseline=baseline,
#         f_do=f_do,
#         feature_names=feature_names,
#         standard_errors=standard_errors,
#         confidence_intervals=confidence_intervals,
#         intervention_values=intervention_values,
#         n_samples=K,
#     )


# __all__ = ["attribute_cai"]


"""CAI attribution from the verified notebook."""

import numpy as np

from .results import CAIResult


def attribute_cai(
    model,
    x_obs,
    feature_names=None,
    verbose=False,
):
    """
    Compute:

        CAI_j =
        E[f(X) | do(X_j=x_j)] - E[f(X)]

    using the notebook's common-random-number estimator.
    """
    anm = model.anm_

    x_obs = np.asarray(
        x_obs,
        dtype=float,
    ).reshape(-1)

    rng = np.random.default_rng(
        model.random_state
    )

    def predict_samples(samp):
        predictions = np.asarray(
            model._f(samp)
        )

        return np.asarray(
            predictions[:, 1]
            if predictions.ndim == 2
            else predictions,
            dtype=float,
        )

    u_noise = np.zeros(
        (
            model.K_cai,
            anm.p,
        ),
        dtype=float,
    )

    for j in anm.order:
        loc, scale = anm.noise[j]

        u_noise[:, j] = rng.laplace(
            loc=loc,
            scale=scale,
            size=model.K_cai,
        )

    baseline_predictions = predict_samples(
        anm.do_sample(
            {},
            K=model.K_cai,
            u_noise=u_noise,
        )
    )

    baseline = float(
        np.mean(
            baseline_predictions
        )
    )

    f_do = np.zeros(
        anm.p,
        dtype=float,
    )

    standard_errors = np.zeros(
        anm.p,
        dtype=float,
    )

    confidence_intervals = np.zeros(
        (anm.p, 2),
        dtype=float,
    )

    unpaired_standard_errors = np.zeros(
        anm.p,
        dtype=float,
    )

    variance_reduction_ratios = np.zeros(
        anm.p,
        dtype=float,
    )

    intervention_values = []

    for j in range(anm.p):
        intervention_predictions = (
            predict_samples(
                anm.do_sample(
                    {j: float(x_obs[j])},
                    K=model.K_cai,
                    u_noise=u_noise,
                )
            )
        )

        # The notebook's result object stores the
        # intervention value itself, not prediction samples.
        intervention_values.append(
            float(x_obs[j])
        )

        intervention_mean = float(
            np.mean(
                intervention_predictions
            )
        )

        f_do[j] = intervention_mean

        paired_diffs = (
            intervention_predictions
            - baseline_predictions
        )

        cai_j = float(
            np.mean(paired_diffs)
        )

        se_paired = float(
            np.std(
                paired_diffs,
                ddof=1,
            )
            / np.sqrt(model.K_cai)
        )

        standard_errors[j] = se_paired

        confidence_intervals[j] = (
            cai_j - 1.96 * se_paired,
            cai_j + 1.96 * se_paired,
        )

        var_diff = float(
            np.var(
                paired_diffs,
                ddof=1,
            )
        )

        var_indep = float(
            np.var(
                intervention_predictions,
                ddof=1,
            )
            + np.var(
                baseline_predictions,
                ddof=1,
            )
        )

        se_unpaired = float(
            np.sqrt(
                var_indep / model.K_cai
            )
        )

        unpaired_standard_errors[j] = (
            se_unpaired
        )

        variance_reduction_ratios[j] = (
            float(
                var_diff / var_indep
            )
            if var_indep > 1e-12
            else 1.0
        )

    cai = f_do - baseline

    cai_norm = cai / (
        np.abs(cai).sum()
        + 1e-8
    )

    return CAIResult(
        x_obs=x_obs,
        cai=cai,
        cai_norm=cai_norm,
        baseline=baseline,
        f_do=f_do,
        feature_names=feature_names,
        standard_errors=standard_errors,
        confidence_intervals=confidence_intervals,
        intervention_values=intervention_values,
        n_samples=model.K_cai,
        unpaired_standard_errors=(
            unpaired_standard_errors
        ),
        variance_reduction_ratios=(
            variance_reduction_ratios
        ),
    )


__all__ = [
    "attribute_cai",
]
