
# # import numpy as np


# # def compare_cai_shap(anm, f, x_obs, K=200, verbose=True):
# #     """
# #     Direct comparison: CAI (do-calculus) vs SHAP-style (observational).

# #     SHAP:
# #         phi_j ≈ E[f(X)|X_j=x_j] - E[f(X)]

# #     CAI:
# #         CAI_j = E[f|do(X_j=x_j)] - E[f(X)]

# #     These diverge whenever X_j has a confounder.
# #     """

# #     x_obs = np.asarray(x_obs, dtype=float).ravel()
# #     p = anm.p

# #     def predict(samp):
# #         pr = f(samp)

# #         if pr.ndim == 2:
# #             pr = pr[:, 1]

# #         return float(pr.mean())

# #     # ============================================================
# #     # CAI: interventional
# #     # ============================================================

# #     baseline_int = predict(
# #         anm.do_sample({}, K=K)
# #     )

# #     cai = np.array([
# #         predict(
# #             anm.do_sample(
# #                 {j: float(x_obs[j])},
# #                 K=K
# #             )
# #         ) - baseline_int
# #         for j in range(p)
# #     ])

# #     # ============================================================
# #     # SHAP-style: observational kernel smoothing
# #     # ============================================================

# #     def obs_exp(j, x_j):

# #         samp = anm.do_sample(
# #             {},
# #             K=K
# #         )

# #         sigma = max(
# #             float(anm.noise[j][1]),
# #             1e-6
# #         )

# #         w = np.exp(
# #             -0.5
# #             * ((samp[:, j] - x_j) / sigma) ** 2
# #         )

# #         preds = f(samp)

# #         if preds.ndim == 2:
# #             preds = preds[:, 1]

# #         # Handle numerical underflow
# #         if w.sum() < 1e-12:
# #             return float(np.mean(preds))

# #         return float(
# #             np.average(
# #                 preds,
# #                 weights=w
# #             )
# #         )

# #     baseline_obs = predict(
# #         anm.do_sample(
# #             {},
# #             K=K
# #         )
# #     )

# #     phi_obs = np.array([
# #         obs_exp(
# #             j,
# #             x_obs[j]
# #         )
# #         for j in range(p)
# #     ]) - baseline_obs

# #     # ============================================================
# #     # Display — SAME FORMAT AS NOTEBOOK
# #     # ============================================================

# #     if verbose:

# #         print("\n" + "=" * 60)
# #         print(
# #             "  CAI (do-calculus) vs SHAP-style (observational)"
# #         )
# #         print("=" * 60)

# #         print(
# #             f"  {'Feature':<10} "
# #             f"{'CAI (do)':>12} "
# #             f"{'SHAP (obs)':>12} "
# #             f"{'Diff':>10} "
# #             f"{'bias?':>7}"
# #         )

# #         print(f"  {'─' * 54}")

# #         for j in range(p):

# #             diff = cai[j] - phi_obs[j]

# #             flag = (
# #                 "  ⚠ *"
# #                 if abs(diff) > 0.05
# #                 else ""
# #             )

# #             print(
# #                 f"  X{j + 1:<9} "
# #                 f"{cai[j]:>+12.4f} "
# #                 f"{phi_obs[j]:>+12.4f} "
# #                 f"{diff:>+10.4f}"
# #                 f"{flag}"
# #             )

# #         n_biased = sum(
# #             abs(cai[j] - phi_obs[j]) > 0.05
# #             for j in range(p)
# #         )

# #         print(
# #             f"\n  ⚠ * = significant confounding bias  "
# #             f"({n_biased}/{p} features)"
# #         )

# #         print(
# #             "  CAI corrects this via the do() operator "
# #             "(Pearl 2009)"
# #         )

# #     return dict(
# #         cai=cai,
# #         shap_style=phi_obs,
# #         baseline_int=baseline_int,
# #         baseline_obs=baseline_obs,
# #     )



# import numpy as np


# def compare_cai_shap(
#     anm,
#     f,
#     x_obs,
#     K=200,
#     verbose=True,
#     random_state=42,
#     bias_threshold=0.05,
# ):
#     """
#     Direct comparison of:

#         CAI:
#             E[f(X) | do(X_j = x_j)] - E[f(X)]

#         SHAP-style observational estimate:
#             E[f(X) | X_j ≈ x_j] - E[f(X)]

#     CAI estimates the interventional effect, while the SHAP-style
#     quantity estimates an observational conditional effect using
#     kernel weighting.

#     The CAI calculation uses common random numbers (CRN): the same
#     exogenous noise is reused for the baseline and every intervention.
#     This reduces Monte Carlo noise when comparing intervention effects.

#     Parameters
#     ----------
#     anm : fitted ANM
#         Fitted additive noise model.

#     f : callable
#         Black-box prediction function.

#     x_obs : array-like
#         Observation at which feature effects are evaluated.

#     K : int, default=200
#         Number of Monte Carlo samples.

#     verbose : bool, default=True
#         Preserve notebook-style diagnostic output.

#     random_state : int, default=42
#         Deterministic random seed.

#     bias_threshold : float, default=0.05
#         Absolute CAI-vs-SHAP-style difference above which a feature
#         is flagged as having substantial disagreement.

#     Returns
#     -------
#     dict
#         Existing outputs are preserved:

#             cai
#             shap_style
#             baseline_int
#             baseline_obs

#         Additional diagnostics:

#             difference
#             n_biased
#             bias_threshold
#             bias_rate
#             mean_abs_difference
#             max_abs_difference
#     """

#     # ============================================================
#     # Input validation
#     # ============================================================

#     K = int(K)

#     if K <= 0:
#         raise ValueError("K must be a positive integer.")

#     x_obs = np.asarray(x_obs, dtype=float).ravel()

#     if not np.all(np.isfinite(x_obs)):
#         raise ValueError("x_obs must contain only finite values.")

#     p = int(anm.p)

#     if len(x_obs) != p:
#         raise ValueError(
#             f"x_obs must contain exactly {p} features; "
#             f"received {len(x_obs)}."
#         )

#     rng = np.random.default_rng(random_state)

#     # ============================================================
#     # Prediction helper
#     # ============================================================

#     def predict(samp):
#         samp = np.asarray(samp, dtype=float)

#         if samp.ndim != 2:
#             raise ValueError(
#                 "ANM samples must be a 2-dimensional array."
#             )

#         preds = np.asarray(f(samp))

#         if preds.ndim == 2:
#             if preds.shape[1] < 2:
#                 preds = preds[:, 0]
#             else:
#                 preds = preds[:, 1]

#         preds = preds.reshape(-1)

#         if len(preds) != len(samp):
#             raise ValueError(
#                 "Black-box prediction count does not match "
#                 "the number of samples."
#             )

#         if not np.all(np.isfinite(preds)):
#             raise ValueError(
#                 "Black-box predictions contain non-finite values."
#             )

#         return preds

#     def predict_mean(samp):
#         return float(np.mean(predict(samp)))

#     # ============================================================
#     # Common random numbers for CAI
#     # ============================================================
#     #
#     # Generate one fixed exogenous-noise realization for every
#     # structural equation and reuse it for baseline/interventions.
#     #
#     # This follows the verified notebook CRN approach.
#     # ============================================================

#     u_noise = {}

#     for j in anm.order:

#         loc, scale = anm.noise[j]

#         scale = max(float(scale), 1e-12)

#         u_noise[j] = rng.laplace(
#             loc=float(loc),
#             scale=scale,
#             size=K,
#         )

#     # ============================================================
#     # CAI: interventional
#     # ============================================================

#     baseline_samples = anm.do_sample(
#         {},
#         K=K,
#         u_noise=u_noise,
#     )

#     baseline_predictions = predict(
#         baseline_samples
#     )

#     baseline_int = float(
#         np.mean(baseline_predictions)
#     )

#     cai = np.empty(p, dtype=float)

#     for j in range(p):

#         intervention_samples = anm.do_sample(
#             {j: float(x_obs[j])},
#             K=K,
#             u_noise=u_noise,
#         )

#         intervention_predictions = predict(
#             intervention_samples
#         )

#         # Paired interventional effect using CRN.
#         paired_difference = (
#             intervention_predictions
#             - baseline_predictions
#         )

#         cai[j] = float(
#             np.mean(paired_difference)
#         )

#     # ============================================================
#     # SHAP-style: observational kernel smoothing
#     # ============================================================

#     # One observational sample is generated and reused for the
#     # feature-wise conditional estimates.
#     observational_samples = anm.do_sample(
#         {},
#         K=K,
#     )

#     observational_predictions = predict(
#         observational_samples
#     )

#     baseline_obs = float(
#         np.mean(observational_predictions)
#     )

#     def obs_exp(j, x_j):

#         sigma = max(
#             float(anm.noise[j][1]),
#             1e-6,
#         )

#         weights = np.exp(
#             -0.5
#             * (
#                 (observational_samples[:, j] - x_j)
#                 / sigma
#             ) ** 2
#         )

#         # Handle numerical underflow.
#         if (
#             not np.all(np.isfinite(weights))
#             or weights.sum() < 1e-12
#         ):
#             return float(
#                 np.mean(observational_predictions)
#             )

#         return float(
#             np.average(
#                 observational_predictions,
#                 weights=weights,
#             )
#         )

#     phi_obs = np.array(
#         [
#             obs_exp(
#                 j,
#                 x_obs[j],
#             )
#             for j in range(p)
#         ],
#         dtype=float,
#     ) - baseline_obs

#     # ============================================================
#     # CAI vs SHAP-style disagreement diagnostics
#     # ============================================================

#     difference = cai - phi_obs

#     abs_difference = np.abs(
#         difference
#     )

#     biased_mask = (
#         abs_difference > float(bias_threshold)
#     )

#     n_biased = int(
#         np.sum(biased_mask)
#     )

#     bias_rate = float(
#         n_biased / p
#     ) if p else 0.0

#     mean_abs_difference = float(
#         np.mean(abs_difference)
#     ) if p else 0.0

#     max_abs_difference = float(
#         np.max(abs_difference)
#     ) if p else 0.0

#     # ============================================================
#     # Display — SAME NOTEBOOK FORMAT
#     # ============================================================

#     if verbose:

#         print("\n" + "=" * 60)
#         print(
#             "  CAI (do-calculus) vs SHAP-style (observational)"
#         )
#         print("=" * 60)

#         print(
#             f"  {'Feature':<10} "
#             f"{'CAI (do)':>12} "
#             f"{'SHAP (obs)':>12} "
#             f"{'Diff':>10} "
#             f"{'bias?':>7}"
#         )

#         print(
#             f"  {'─' * 54}"
#         )

#         for j in range(p):

#             diff = difference[j]

#             flag = (
#                 "  ⚠ *"
#                 if abs(diff) > bias_threshold
#                 else ""
#             )

#             print(
#                 f"  X{j + 1:<9} "
#                 f"{cai[j]:>+12.4f} "
#                 f"{phi_obs[j]:>+12.4f} "
#                 f"{diff:>+10.4f}"
#                 f"{flag}"
#             )

#         print(
#             f"\n  ⚠ * = significant confounding bias  "
#             f"({n_biased}/{p} features)"
#         )

#         print(
#             "  CAI corrects this via the do() operator "
#             "(Pearl 2009)"
#         )

#     # ============================================================
#     # Return
#     # ============================================================

#     return dict(
#         # Existing API
#         cai=cai,
#         shap_style=phi_obs,
#         baseline_int=baseline_int,
#         baseline_obs=baseline_obs,

#         # Notebook diagnostics
#         difference=difference,
#         n_biased=n_biased,
#         bias_threshold=float(bias_threshold),
#         bias_rate=bias_rate,
#         mean_abs_difference=mean_abs_difference,
#         max_abs_difference=max_abs_difference,
#     )


# __all__ = [
#     "compare_cai_shap",
# ]

"""CAI vs SHAP-style comparison from the verified notebook."""

import numpy as np


def compare_cai_shap(
    anm,
    f,
    x_obs,
    K=200,
    verbose=True,
):
    """
    Direct comparison:

        SHAP-style:
            E[f(X) | X_j=x_j] - E[f(X)]

        CAI:
            E[f(X) | do(X_j=x_j)] - E[f(X)]
    """
    p = anm.p

    x_obs = np.asarray(
        x_obs,
        dtype=float,
    ).reshape(-1)

    def predict(samp):
        predictions = np.asarray(
            f(samp)
        )

        if predictions.ndim == 2:
            predictions = predictions[:, 1]

        return float(
            np.mean(predictions)
        )

    baseline_int = predict(
        anm.do_sample(
            {},
            K=K,
        )
    )

    cai = np.array([
        predict(
            anm.do_sample(
                {
                    j: float(
                        x_obs[j]
                    )
                },
                K=K,
            )
        ) - baseline_int
        for j in range(p)
    ])

    def obs_exp(j, x_j):
        samp = anm.do_sample(
            {},
            K=K,
        )

        sigma = max(
            float(
                anm.noise[j][1]
            ),
            1e-6,
        )

        weights = np.exp(
            -0.5
            * (
                (
                    samp[:, j] - x_j
                )
                / sigma
            ) ** 2
        )

        predictions = np.asarray(
            f(samp)
        )

        if predictions.ndim == 2:
            predictions = predictions[:, 1]

        if weights.sum() < 1e-12:
            return float(
                np.mean(predictions)
            )

        return float(
            np.average(
                predictions,
                weights=weights,
            )
        )

    baseline_obs = predict(
        anm.do_sample(
            {},
            K=K,
        )
    )

    phi_obs = np.array([
        obs_exp(
            j,
            x_obs[j],
        )
        for j in range(p)
    ]) - baseline_obs

    if verbose:
        print(
            "\n" + "=" * 60
        )
        print(
            "  CAI (do-calculus) vs "
            "SHAP-style (observational)"
        )
        print(
            "=" * 60
        )
        print(
            f"  {'Feature':<10} "
            f"{'CAI (do)':>12} "
            f"{'SHAP (obs)':>12} "
            f"{'Diff':>10} "
            f"{'bias?':>7}"
        )
        print(
            f"  {'─' * 54}"
        )

        for j in range(p):
            diff = (
                cai[j]
                - phi_obs[j]
            )

            flag = (
                "  ⚠ *"
                if abs(diff) > 0.05
                else ""
            )

            print(
                f"  X{j + 1:<9} "
                f"{cai[j]:>+12.4f} "
                f"{phi_obs[j]:>+12.4f} "
                f"{diff:>+10.4f}"
                f"{flag}"
            )

        n_biased = sum(
            abs(
                cai[j]
                - phi_obs[j]
            ) > 0.05
            for j in range(p)
        )

        print(
            f"\n  ⚠ * = significant confounding bias  "
            f"({n_biased}/{p} features)"
        )

        print(
            "  CAI corrects this via the do() "
            "operator (Pearl 2009)"
        )

    return {
        "cai": cai,
        "shap_style": phi_obs,
        "baseline_int": baseline_int,
        "baseline_obs": baseline_obs,
    }


__all__ = [
    "compare_cai_shap",
]
