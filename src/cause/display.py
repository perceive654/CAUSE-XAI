
# # # # # """
# # # # # User-facing display layer for CAUSE-XAI.

# # # # # The display layer converts CAUSE-XAI results into
# # # # # human-readable tables, charts, and explanations.

# # # # # Public functions
# # # # # ----------------
# # # # # show_fit()
# # # # # show_counterfactual()
# # # # # show_attribution()
# # # # # show_explanation()
# # # # # show_cai_vs_shap()
# # # # # display()

# # # # # Important
# # # # # ---------
# # # # # This module does not require a task/classification/regression
# # # # # argument. It displays the numerical outputs produced by the
# # # # # CAUSE-XAI methods directly.
# # # # # """

# # # # # import numpy as np

# # # # # from .results import (
# # # # #     CCEResult,
# # # # #     CAIResult,
# # # # #     UnifiedExplanation,
# # # # # )


# # # # # # ================================================================
# # # # # # OPTIONAL VISUALIZATION DEPENDENCY
# # # # # # ================================================================

# # # # # def _get_plt():
# # # # #     """
# # # # #     Import matplotlib only when a graphical display is requested.
# # # # #     """
# # # # #     try:
# # # # #         import matplotlib.pyplot as plt
# # # # #         return plt
# # # # #     except ImportError as exc:
# # # # #         raise ImportError(
# # # # #             "CAUSE-XAI graphical displays require matplotlib.\n"
# # # # #             "Install it with:\n"
# # # # #             "    pip install matplotlib"
# # # # #         ) from exc


# # # # # # ================================================================
# # # # # # BASIC HELPERS
# # # # # # ================================================================

# # # # # def _names(values, feature_names=None):
# # # # #     """Return readable feature names."""

# # # # #     n = len(values)

# # # # #     if feature_names is not None:

# # # # #         if len(feature_names) != n:
# # # # #             raise ValueError(
# # # # #                 "feature_names must have the same length "
# # # # #                 "as the number of features."
# # # # #             )

# # # # #         return list(feature_names)

# # # # #     return [
# # # # #         f"Feature {i + 1}"
# # # # #         for i in range(n)
# # # # #     ]


# # # # # def _line(char="─", width=78):
# # # # #     print(char * width)


# # # # # def _header(title, width=78):
# # # # #     print()
# # # # #     print("═" * width)
# # # # #     print(title.center(width))
# # # # #     print("═" * width)


# # # # # def _format_change(old, new):
# # # # #     """
# # # # #     Convert a numerical change into readable language.
# # # # #     """

# # # # #     delta = float(new) - float(old)

# # # # #     if abs(delta) < 1e-10:
# # # # #         return "No change"

# # # # #     if delta > 0:
# # # # #         return f"Increase by {abs(delta):.3f}"

# # # # #     return f"Decrease by {abs(delta):.3f}"


# # # # # def _format_ci(ci):
# # # # #     """Format a confidence interval."""

# # # # #     return (
# # # # #         f"[{float(ci[0]):+.4f}, "
# # # # #         f"{float(ci[1]):+.4f}]"
# # # # #     )


# # # # # def _effect_description(effect):
# # # # #     """
# # # # #     Human-readable CAI interpretation.

# # # # #     This remains intentionally generic because the
# # # # #     underlying model output may be a probability or
# # # # #     a regression value.
# # # # #     """

# # # # #     effect = float(effect)

# # # # #     if abs(effect) < 1e-10:
# # # # #         return "Little measurable influence"

# # # # #     magnitude = abs(effect)

# # # # #     if effect > 0:

# # # # #         if magnitude >= 0.20:
# # # # #             return "Strong increase"

# # # # #         if magnitude >= 0.10:
# # # # #             return "Moderate increase"

# # # # #         return "Small increase"

# # # # #     if magnitude >= 0.20:
# # # # #         return "Strong decrease"

# # # # #     if magnitude >= 0.10:
# # # # #         return "Moderate decrease"

# # # # #     return "Small decrease"


# # # # # def _direction_sentence(feature, effect):
# # # # #     """Natural-language causal direction."""

# # # # #     effect = float(effect)

# # # # #     if effect > 0:

# # # # #         return (
# # # # #             f"{feature} has the strongest estimated causal "
# # # # #             f"influence and increases the expected model output."
# # # # #         )

# # # # #     if effect < 0:

# # # # #         return (
# # # # #             f"{feature} has the strongest estimated causal "
# # # # #             f"influence and decreases the expected model output."
# # # # #         )

# # # # #     return (
# # # # #         f"{feature} has little measurable causal influence "
# # # # #         f"on the expected model output."
# # # # #     )


# # # # # def _safe_float(value):
# # # # #     """Convert scalar-like value to float."""

# # # # #     try:
# # # # #         return float(value)
# # # # #     except Exception:
# # # # #         return value


# # # # # # ================================================================
# # # # # # GRAPHICAL TABLE HELPER
# # # # # # ================================================================

# # # # # def _show_table(
# # # # #     rows,
# # # # #     columns,
# # # # #     title=None,
# # # # #     figsize=None,
# # # # #     font_size=9,
# # # # # ):
# # # # #     """
# # # # #     Display an actual matplotlib table.

# # # # #     Parameters
# # # # #     ----------
# # # # #     rows : list[list]
# # # # #         Table rows.
# # # # #     columns : list[str]
# # # # #         Column headings.
# # # # #     """

# # # # #     plt = _get_plt()

# # # # #     if figsize is None:

# # # # #         width = max(
# # # # #             9,
# # # # #             len(columns) * 1.5,
# # # # #         )

# # # # #         height = max(
# # # # #             2.5,
# # # # #             min(14, 1.0 + 0.42 * len(rows)),
# # # # #         )

# # # # #         figsize = (
# # # # #             width,
# # # # #             height,
# # # # #         )

# # # # #     fig, ax = plt.subplots(
# # # # #         figsize=figsize
# # # # #     )

# # # # #     ax.axis("off")

# # # # #     if title is not None:
# # # # #         ax.set_title(
# # # # #             title,
# # # # #             fontsize=13,
# # # # #             pad=16,
# # # # #             fontweight="bold",
# # # # #         )

# # # # #     table = ax.table(
# # # # #         cellText=rows,
# # # # #         colLabels=columns,
# # # # #         loc="center",
# # # # #         cellLoc="center",
# # # # #     )

# # # # #     table.auto_set_font_size(False)
# # # # #     table.set_fontsize(font_size)
# # # # #     table.scale(
# # # # #         1,
# # # # #         1.6,
# # # # #     )

# # # # #     plt.tight_layout()
# # # # #     plt.show()

# # # # #     return fig


# # # # # # ================================================================
# # # # # # METRIC CARD DISPLAY
# # # # # # ================================================================

# # # # # def _show_metric_cards(metrics):
# # # # #     """
# # # # #     Display causal metrics as a compact visual dashboard.

# # # # #     metrics:
# # # # #         list of dictionaries with:
# # # # #             title
# # # # #             value
# # # # #             explanation
# # # # #     """

# # # # #     plt = _get_plt()

# # # # #     n = len(metrics)

# # # # #     cols = 3
# # # # #     rows = int(
# # # # #         np.ceil(n / cols)
# # # # #     )

# # # # #     fig = plt.figure(
# # # # #         figsize=(
# # # # #             13,
# # # # #             3.0 * rows,
# # # # #         )
# # # # #     )

# # # # #     for i, metric in enumerate(metrics):

# # # # #         ax = fig.add_subplot(
# # # # #             rows,
# # # # #             cols,
# # # # #             i + 1,
# # # # #         )

# # # # #         ax.axis("off")

# # # # #         title = metric["title"]
# # # # #         value = metric["value"]
# # # # #         explanation = metric["explanation"]

# # # # #         ax.text(
# # # # #             0.5,
# # # # #             0.76,
# # # # #             title,
# # # # #             ha="center",
# # # # #             va="center",
# # # # #             fontsize=11,
# # # # #             fontweight="bold",
# # # # #         )

# # # # #         ax.text(
# # # # #             0.5,
# # # # #             0.50,
# # # # #             value,
# # # # #             ha="center",
# # # # #             va="center",
# # # # #             fontsize=22,
# # # # #             fontweight="bold",
# # # # #         )

# # # # #         ax.text(
# # # # #             0.5,
# # # # #             0.19,
# # # # #             explanation,
# # # # #             ha="center",
# # # # #             va="center",
# # # # #             fontsize=8.5,
# # # # #             wrap=True,
# # # # #         )

# # # # #         for spine in ax.spines.values():
# # # # #             spine.set_visible(True)

# # # # #     # Hide unused axes.

# # # # #     total = rows * cols

# # # # #     for i in range(n, total):

# # # # #         ax = fig.add_subplot(
# # # # #             rows,
# # # # #             cols,
# # # # #             i + 1,
# # # # #         )

# # # # #         ax.axis("off")

# # # # #     plt.tight_layout()
# # # # #     plt.show()

# # # # #     return fig


# # # # # # ================================================================
# # # # # # PREDICTION TRANSITION VISUAL
# # # # # # ================================================================

# # # # # def _show_prediction_transition(
# # # # #     current,
# # # # #     achieved,
# # # # #     target=None,
# # # # #     title="Prediction change",
# # # # # ):
# # # # #     """
# # # # #     Show the movement from current model output
# # # # #     to the achieved counterfactual output.
# # # # #     """

# # # # #     plt = _get_plt()

# # # # #     current = float(current)
# # # # #     achieved = float(achieved)

# # # # #     fig, ax = plt.subplots(
# # # # #         figsize=(11, 3.8)
# # # # #     )

# # # # #     minimum = min(
# # # # #         current,
# # # # #         achieved,
# # # # #     )

# # # # #     maximum = max(
# # # # #         current,
# # # # #         achieved,
# # # # #     )

# # # # #     span = max(
# # # # #         abs(maximum - minimum),
# # # # #         1e-6,
# # # # #     )

# # # # #     left = minimum - 0.15 * span
# # # # #     right = maximum + 0.15 * span

# # # # #     ax.set_xlim(
# # # # #         left,
# # # # #         right,
# # # # #     )

# # # # #     ax.set_ylim(
# # # # #         -0.8,
# # # # #         0.8,
# # # # #     )

# # # # #     ax.axhline(
# # # # #         0,
# # # # #         linewidth=2,
# # # # #     )

# # # # #     ax.scatter(
# # # # #         [current],
# # # # #         [0],
# # # # #         s=120,
# # # # #         zorder=5,
# # # # #     )

# # # # #     ax.scatter(
# # # # #         [achieved],
# # # # #         [0],
# # # # #         s=120,
# # # # #         zorder=5,
# # # # #     )

# # # # #     ax.annotate(
# # # # #         f"Current\n{current:.4f}",
# # # # #         xy=(current, 0),
# # # # #         xytext=(current, 0.45),
# # # # #         ha="center",
# # # # #         arrowprops=dict(
# # # # #             arrowstyle="->",
# # # # #         ),
# # # # #     )

# # # # #     ax.annotate(
# # # # #         f"After change\n{achieved:.4f}",
# # # # #         xy=(achieved, 0),
# # # # #         xytext=(achieved, -0.50),
# # # # #         ha="center",
# # # # #         arrowprops=dict(
# # # # #             arrowstyle="->",
# # # # #         ),
# # # # #     )

# # # # #     ax.annotate(
# # # # #         "",
# # # # #         xy=(achieved, 0),
# # # # #         xytext=(current, 0),
# # # # #         arrowprops=dict(
# # # # #             arrowstyle="<->",
# # # # #             linewidth=2,
# # # # #         ),
# # # # #     )

# # # # #     delta = achieved - current

# # # # #     midpoint = (
# # # # #         current + achieved
# # # # #     ) / 2

# # # # #     ax.text(
# # # # #         midpoint,
# # # # #         0.13,
# # # # #         f"Change: {delta:+.4f}",
# # # # #         ha="center",
# # # # #         fontsize=11,
# # # # #         fontweight="bold",
# # # # #     )

# # # # #     if target is not None:

# # # # #         ax.axvline(
# # # # #             float(target),
# # # # #             linestyle="--",
# # # # #             linewidth=1.5,
# # # # #         )

# # # # #         ax.text(
# # # # #             float(target),
# # # # #             0.68,
# # # # #             f"Target\n{float(target):.4f}",
# # # # #             ha="center",
# # # # #             fontsize=9,
# # # # #         )

# # # # #     ax.set_title(
# # # # #         title,
# # # # #         fontsize=13,
# # # # #         fontweight="bold",
# # # # #     )

# # # # #     ax.set_yticks([])

# # # # #     ax.set_xlabel(
# # # # #         "Model output"
# # # # #     )

# # # # #     plt.tight_layout()
# # # # #     plt.show()

# # # # #     return fig


# # # # # # ================================================================
# # # # # # 1. COUNTERFACTUAL DISPLAY
# # # # # # ================================================================

# # # # # def show_counterfactual(
# # # # #     result: CCEResult,
# # # # #     feature_names=None,
# # # # # ):
# # # # #     """
# # # # #     Display a user-facing causal counterfactual.

# # # # #     Shows:

# # # # #         1. Prediction transition
# # # # #         2. Causal metric cards
# # # # #         3. Direct interventions
# # # # #         4. Downstream effects
# # # # #         5. Technical counterfactual table
# # # # #     """

# # # # #     names = _names(
# # # # #         result.x_obs,
# # # # #         feature_names,
# # # # #     )

# # # # #     _header(
# # # # #         "COUNTERFACTUAL EXPLANATION"
# # # # #     )

# # # # #     # ============================================================
# # # # #     # 1. Prediction summary
# # # # #     # ============================================================

# # # # #     print("\nWHAT WOULD NEED TO CHANGE?")
# # # # #     _line()

# # # # #     print(
# # # # #         f"  Current model output : "
# # # # #         f"{result.y_fact:.4f}"
# # # # #     )

# # # # #     print(
# # # # #         f"  Requested target     : "
# # # # #         f"{result.y_foil:.4f}"
# # # # #     )

# # # # #     print(
# # # # #         f"  Achieved output      : "
# # # # #         f"{result.y_achieved:.4f}"
# # # # #     )

# # # # #     if result.feasible:

# # # # #         print(
# # # # #             "\n  ✓ A feasible counterfactual was found."
# # # # #         )

# # # # #     else:

# # # # #         print(
# # # # #             "\n  ✗ The requested target was not reached."
# # # # #         )

# # # # #     # Graphical prediction transition.

# # # # #     _show_prediction_transition(
# # # # #         result.y_fact,
# # # # #         result.y_achieved,
# # # # #         target=result.y_foil,
# # # # #         title="Counterfactual prediction change",
# # # # #     )

# # # # #     # ============================================================
# # # # #     # 2. Causal metrics
# # # # #     # ============================================================

# # # # #     direct = (
# # # # #         result.direct_interventions
# # # # #         or []
# # # # #     )

# # # # #     changed = (
# # # # #         result.changed
# # # # #         or []
# # # # #     )

# # # # #     downstream = [
# # # # #         j
# # # # #         for j in changed
# # # # #         if j not in direct
# # # # #     ]

# # # # #     total_features = len(
# # # # #         result.x_obs
# # # # #     )

# # # # #     direct_count = len(
# # # # #         direct
# # # # #     )

# # # # #     downstream_count = len(
# # # # #         downstream
# # # # #     )

# # # # #     sparsity = float(
# # # # #         result.sparsity
# # # # #     )

# # # # #     violation = float(
# # # # #         result.violation
# # # # #     )

# # # # #     distance = float(
# # # # #         result.d_causal
# # # # #     )

# # # # #     violation_ok = (
# # # # #         violation < 1.5
# # # # #     )

# # # # #     metrics = [

# # # # #         {
# # # # #             "title": "DIRECT INTERVENTIONS",
# # # # #             "value": f"{direct_count} / {total_features}",
# # # # #             "explanation": (
# # # # #                 "Features intentionally changed\n"
# # # # #                 "to obtain the counterfactual."
# # # # #             ),
# # # # #         },

# # # # #         {
# # # # #             "title": "DOWNSTREAM CHANGES",
# # # # #             "value": str(downstream_count),
# # # # #             "explanation": (
# # # # #                 "Additional features that changed\n"
# # # # #                 "because of causal propagation."
# # # # #             ),
# # # # #         },

# # # # #         {
# # # # #             "title": "CAUSAL SPARSITY",
# # # # #             "value": f"{sparsity * 100:.1f}%",
# # # # #             "explanation": (
# # # # #                 "How concentrated the solution is.\n"
# # # # #                 "Higher means fewer direct changes."
# # # # #             ),
# # # # #         },

# # # # #         {
# # # # #             "title": "CAUSAL CONSISTENCY",
# # # # #             "value": (
# # # # #                 "✓ Consistent"
# # # # #                 if violation_ok
# # # # #                 else "⚠ Check"
# # # # #             ),
# # # # #             "explanation": (
# # # # #                 f"Constraint score: {violation:.4f}\n"
# # # # #                 "Lower indicates better consistency."
# # # # #             ),
# # # # #         },

# # # # #         {
# # # # #             "title": "CAUSAL DISTANCE",
# # # # #             "value": f"{distance:.4f}",
# # # # #             "explanation": (
# # # # #                 "Distance of the counterfactual\n"
# # # # #                 "from the observed causal state."
# # # # #             ),
# # # # #         },

# # # # #         {
# # # # #             "title": "RUNTIME",
# # # # #             "value": f"{float(result.runtime):.2f} s",
# # # # #             "explanation": (
# # # # #                 "Time required to find\n"
# # # # #                 "the counterfactual."
# # # # #             ),
# # # # #         },
# # # # #     ]

# # # # #     _show_metric_cards(
# # # # #         metrics
# # # # #     )

# # # # #     # ============================================================
# # # # #     # 3. Direct interventions
# # # # #     # ============================================================

# # # # #     print("\nDIRECT INTERVENTIONS")
# # # # #     _line()

# # # # #     if direct:

# # # # #         rows = []

# # # # #         for j in direct:

# # # # #             old = float(
# # # # #                 result.x_obs[j]
# # # # #             )

# # # # #             new = float(
# # # # #                 result.x_star[j]
# # # # #             )

# # # # #             delta = new - old

# # # # #             rows.append(
# # # # #                 [
# # # # #                     names[j],
# # # # #                     f"{old:.4f}",
# # # # #                     f"{new:.4f}",
# # # # #                     f"{delta:+.4f}",
# # # # #                     _format_change(
# # # # #                         old,
# # # # #                         new,
# # # # #                     ),
# # # # #                 ]
# # # # #             )

# # # # #         _show_table(
# # # # #             rows,
# # # # #             [
# # # # #                 "Feature",
# # # # #                 "Current",
# # # # #                 "New value",
# # # # #                 "Change",
# # # # #                 "Required action",
# # # # #             ],
# # # # #             title="Direct causal interventions",
# # # # #         )

# # # # #     else:

# # # # #         print(
# # # # #             "  No direct feature intervention."
# # # # #         )

# # # # #     # ============================================================
# # # # #     # 4. Downstream changes
# # # # #     # ============================================================

# # # # #     print("\nDOWNSTREAM EFFECTS")
# # # # #     _line()

# # # # #     if downstream:

# # # # #         print(
# # # # #             f"  {downstream_count} feature(s) changed "
# # # # #             "as a consequence of the direct intervention."
# # # # #         )

# # # # #         rows = []

# # # # #         for j in downstream:

# # # # #             old = float(
# # # # #                 result.x_obs[j]
# # # # #             )

# # # # #             new = float(
# # # # #                 result.x_star[j]
# # # # #             )

# # # # #             delta = new - old

# # # # #             rows.append(
# # # # #                 [
# # # # #                     names[j],
# # # # #                     f"{old:.4f}",
# # # # #                     f"{new:.4f}",
# # # # #                     f"{delta:+.4f}",
# # # # #                 ]
# # # # #             )

# # # # #         _show_table(
# # # # #             rows,
# # # # #             [
# # # # #                 "Feature",
# # # # #                 "Original",
# # # # #                 "Causal result",
# # # # #                 "Change",
# # # # #             ],
# # # # #             title="Downstream causal changes",
# # # # #         )

# # # # #     else:

# # # # #         print(
# # # # #             "  No downstream feature changes."
# # # # #         )

# # # # #     # ============================================================
# # # # #     # 5. Complete technical table
# # # # #     # ============================================================

# # # # #     print("\nCOUNTERFACTUAL DETAILS")
# # # # #     _line()

# # # # #     rows = []

# # # # #     for j in changed:

# # # # #         old = float(
# # # # #             result.x_obs[j]
# # # # #         )

# # # # #         new = float(
# # # # #             result.x_star[j]
# # # # #         )

# # # # #         role = (
# # # # #             "Direct intervention"
# # # # #             if j in direct
# # # # #             else "Downstream"
# # # # #         )

# # # # #         rows.append(
# # # # #             [
# # # # #                 names[j],
# # # # #                 f"{old:.4f}",
# # # # #                 f"{new:.4f}",
# # # # #                 f"{new - old:+.4f}",
# # # # #                 role,
# # # # #             ]
# # # # #         )

# # # # #     if rows:

# # # # #         _show_table(
# # # # #             rows,
# # # # #             [
# # # # #                 "Feature",
# # # # #                 "Original",
# # # # #                 "Counterfactual",
# # # # #                 "Δ",
# # # # #                 "Causal role",
# # # # #             ],
# # # # #             title="All changed features",
# # # # #         )

# # # # #     print()


# # # # # # ================================================================
# # # # # # 2. CAUSAL FEATURE IMPACT / CAI
# # # # # # ================================================================

# # # # # def show_attribution(
# # # # #     result: CAIResult,
# # # # #     feature_names=None,
# # # # # ):
# # # # #     """
# # # # #     Display CAI attribution.

# # # # #     This section intentionally remains focused on
# # # # #     the CAI attribution representation.

# # # # #     The display provides:
# # # # #         - CAI ranking
# # # # #         - technical uncertainty
# # # # #         - main causal driver
# # # # #         - baseline reference
# # # # #     """

# # # # #     names = _names(
# # # # #         result.x_obs,
# # # # #         feature_names,
# # # # #     )

# # # # #     cai = np.asarray(
# # # # #         result.cai,
# # # # #         dtype=float,
# # # # #     )

# # # # #     if cai.size == 0:

# # # # #         _header(
# # # # #             "CAUSAL FEATURE IMPACT"
# # # # #         )

# # # # #         print(
# # # # #             "\n  No CAI values available."
# # # # #         )

# # # # #         return

# # # # #     order = np.argsort(
# # # # #         np.abs(cai)
# # # # #     )[::-1]

# # # # #     top = int(
# # # # #         order[0]
# # # # #     )

# # # # #     top_effect = float(
# # # # #         cai[top]
# # # # #     )

# # # # #     _header(
# # # # #         "CAUSAL FEATURE IMPACT"
# # # # #     )

# # # # #     print(
# # # # #         "\nThe causal effect estimates how intervening "
# # # # #         "on each feature changes the expected model output."
# # # # #     )

# # # # #     if result.n_samples is not None:

# # # # #         print(
# # # # #             f"\n  Monte Carlo samples : "
# # # # #             f"{result.n_samples}"
# # # # #         )

# # # # #     # ============================================================
# # # # #     # CAI table
# # # # #     # ============================================================

# # # # #     print("\nFeature-level causal effects")
# # # # #     _line()

# # # # #     rows = []

# # # # #     for rank, j in enumerate(order):

# # # # #         j = int(j)

# # # # #         intervention = None

# # # # #         if result.intervention_values is not None:

# # # # #             try:
# # # # #                 intervention = float(
# # # # #                     result.x_obs[j]
# # # # #                 )
# # # # #             except Exception:
# # # # #                 intervention = None

# # # # #         f_do = float(
# # # # #             result.f_do[j]
# # # # #         )

# # # # #         effect = float(
# # # # #             cai[j]
# # # # #         )

# # # # #         se = None

# # # # #         if result.standard_errors is not None:
# # # # #             se = float(
# # # # #                 result.standard_errors[j]
# # # # #             )

# # # # #         ci = None

# # # # #         if result.confidence_intervals is not None:
# # # # #             ci = _format_ci(
# # # # #                 result.confidence_intervals[j]
# # # # #             )

# # # # #         rows.append(
# # # # #             [
# # # # #                 rank + 1,
# # # # #                 names[j],
# # # # #                 (
# # # # #                     f"{intervention:.4f}"
# # # # #                     if intervention is not None
# # # # #                     else "-"
# # # # #                 ),
# # # # #                 f"{f_do:.4f}",
# # # # #                 f"{effect:+.4f}",
# # # # #                 (
# # # # #                     f"{se:.4f}"
# # # # #                     if se is not None
# # # # #                     else "-"
# # # # #                 ),
# # # # #                 ci if ci is not None else "-",
# # # # #             ]
# # # # #         )

# # # # #     _show_table(
# # # # #         rows,
# # # # #         [
# # # # #             "Rank",
# # # # #             "Feature",
# # # # #             "Intervention",
# # # # #             "E[f | do]",
# # # # #             "CAI",
# # # # #             "SE",
# # # # #             "95% CI",
# # # # #         ],
# # # # #         title="Feature-level causal effects",
# # # # #         figsize=(
# # # # #             13,
# # # # #             max(
# # # # #                 4,
# # # # #                 min(
# # # # #                     16,
# # # # #                     1.5 + 0.35 * len(rows),
# # # # #                 ),
# # # # #             ),
# # # # #         ),
# # # # #         font_size=8,
# # # # #     )

# # # # #     # ============================================================
# # # # #     # Main driver
# # # # #     # ============================================================

# # # # #     print("\nMAIN CAUSAL DRIVER")
# # # # #     _line()

# # # # #     print(
# # # # #         f"  {_direction_sentence(names[top], top_effect)}"
# # # # #     )

# # # # #     print(
# # # # #         f"  CAI : {top_effect:+.4f}"
# # # # #     )

# # # # #     print(
# # # # #         f"  Baseline expected output : "
# # # # #         f"{result.baseline:.4f}"
# # # # #     )

# # # # #     print()


# # # # # # ================================================================
# # # # # # 3. UNIFIED EXPLANATION
# # # # # # ================================================================

# # # # # def show_explanation(
# # # # #     explanation: UnifiedExplanation,
# # # # #     feature_names=None,
# # # # # ):
# # # # #     """
# # # # #     Main CAUSE-XAI explanation.

# # # # #     The unified display answers:

# # # # #         1. What is the model predicting?
# # # # #         2. What can change that prediction?
# # # # #         3. Which feature is the strongest causal driver?
# # # # #         4. What happens downstream?
# # # # #         5. Is the counterfactual causally consistent?

# # # # #     The CAI visual itself is intentionally kept separate
# # # # #     from this high-level dashboard.
# # # # #     """

# # # # #     names = _names(
# # # # #         explanation.x_obs,
# # # # #         feature_names,
# # # # #     )

# # # # #     cce = explanation.cce
# # # # #     cai = explanation.cai

# # # # #     cai_values = np.asarray(
# # # # #         cai.cai,
# # # # #         dtype=float,
# # # # #     )

# # # # #     if cai_values.size == 0:

# # # # #         _header(
# # # # #             "CAUSE-XAI — MODEL EXPLANATION"
# # # # #         )

# # # # #         print(
# # # # #             "\n  No causal attribution values available."
# # # # #         )

# # # # #         return

# # # # #     order = np.argsort(
# # # # #         np.abs(cai_values)
# # # # #     )[::-1]

# # # # #     _header(
# # # # #         "CAUSE-XAI — MODEL EXPLANATION"
# # # # #     )

# # # # #     # ============================================================
# # # # #     # 1. HIGH LEVEL PREDICTION
# # # # #     # ============================================================

# # # # #     print("\n1. MODEL OUTPUT")
# # # # #     _line()

# # # # #     print(
# # # # #         f"  Current output : "
# # # # #         f"{explanation.y_fact:.4f}"
# # # # #     )

# # # # #     print(
# # # # #         f"  Target output  : "
# # # # #         f"{explanation.y_foil:.4f}"
# # # # #     )

# # # # #     print(
# # # # #         f"  Achieved output: "
# # # # #         f"{cce.y_achieved:.4f}"
# # # # #     )

# # # # #     if cce.feasible:

# # # # #         print(
# # # # #             "\n  ✓ A feasible causal counterfactual "
# # # # #             "was found."
# # # # #         )

# # # # #     else:

# # # # #         print(
# # # # #             "\n  ✗ The requested target could not "
# # # # #             "be reached."
# # # # #         )

# # # # #     _show_prediction_transition(
# # # # #         explanation.y_fact,
# # # # #         cce.y_achieved,
# # # # #         target=explanation.y_foil,
# # # # #         title="Model output: current → counterfactual",
# # # # #     )

# # # # #     # ============================================================
# # # # #     # 2. EXPLANATION SUMMARY
# # # # #     # ============================================================

# # # # #     top = int(
# # # # #         order[0]
# # # # #     )

# # # # #     top_effect = float(
# # # # #         cai_values[top]
# # # # #     )

# # # # #     direct = (
# # # # #         cce.direct_interventions
# # # # #         or []
# # # # #     )

# # # # #     changed = (
# # # # #         cce.changed
# # # # #         or []
# # # # #     )

# # # # #     downstream = [
# # # # #         j
# # # # #         for j in changed
# # # # #         if j not in direct
# # # # #     ]

# # # # #     print("\n2. WHAT EXPLAINS THE RESULT?")
# # # # #     _line()

# # # # #     print(
# # # # #         f"  Why does the output move?"
# # # # #     )

# # # # #     print(
# # # # #         f"    {names[top]} is the strongest causal driver "
# # # # #         f"with CAI = {top_effect:+.4f}."
# # # # #     )

# # # # #     print(
# # # # #         f"\n  What would need to change?"
# # # # #     )

# # # # #     if direct:

# # # # #         for j in direct:

# # # # #             old = float(
# # # # #                 cce.x_obs[j]
# # # # #             )

# # # # #             new = float(
# # # # #                 cce.x_star[j]
# # # # #             )

# # # # #             print(
# # # # #                 f"    • {names[j]}: "
# # # # #                 f"{old:.4f} → {new:.4f} "
# # # # #                 f"({_format_change(old, new).lower()})"
# # # # #             )

# # # # #     elif changed:

# # # # #         print(
# # # # #             "    The solution changes "
# # # # #             "the following features:"
# # # # #         )

# # # # #         for j in changed[:5]:

# # # # #             old = float(
# # # # #                 cce.x_obs[j]
# # # # #             )

# # # # #             new = float(
# # # # #                 cce.x_star[j]
# # # # #             )

# # # # #             print(
# # # # #                 f"    • {names[j]}: "
# # # # #                 f"{old:.4f} → {new:.4f}"
# # # # #             )

# # # # #     else:

# # # # #         print(
# # # # #             "    No feature change was required."
# # # # #         )

# # # # #     # ============================================================
# # # # #     # 3. CAUSAL METRIC DASHBOARD
# # # # #     # ============================================================

# # # # #     print("\n3. CAUSAL QUALITY")
# # # # #     _line()

# # # # #     violation = float(
# # # # #         cce.violation
# # # # #     )

# # # # #     violation_ok = (
# # # # #         violation < 1.5
# # # # #     )

# # # # #     total_features = len(
# # # # #         explanation.x_obs
# # # # #     )

# # # # #     direct_count = len(
# # # # #         direct
# # # # #     )

# # # # #     downstream_count = len(
# # # # #         downstream
# # # # #     )

# # # # #     metrics = [

# # # # #         {
# # # # #             "title": "DIRECT CHANGES",
# # # # #             "value": f"{direct_count} / {total_features}",
# # # # #             "explanation": (
# # # # #                 "Features deliberately changed\n"
# # # # #                 "to obtain the target."
# # # # #             ),
# # # # #         },

# # # # #         {
# # # # #             "title": "DOWNSTREAM EFFECTS",
# # # # #             "value": str(downstream_count),
# # # # #             "explanation": (
# # # # #                 "Features that changed because\n"
# # # # #                 "of causal propagation."
# # # # #             ),
# # # # #         },

# # # # #         {
# # # # #             "title": "CAUSAL SPARSITY",
# # # # #             "value": (
# # # # #                 f"{float(cce.sparsity) * 100:.1f}%"
# # # # #             ),
# # # # #             "explanation": (
# # # # #                 "Higher means the solution uses\n"
# # # # #                 "fewer direct changes."
# # # # #             ),
# # # # #         },

# # # # #         {
# # # # #             "title": "CAUSAL CONSISTENCY",
# # # # #             "value": (
# # # # #                 "✓ Consistent"
# # # # #                 if violation_ok
# # # # #                 else "⚠ Check"
# # # # #             ),
# # # # #             "explanation": (
# # # # #                 f"Constraint score: {violation:.4f}\n"
# # # # #                 "Lower indicates better consistency."
# # # # #             ),
# # # # #         },

# # # # #         {
# # # # #             "title": "CAUSAL DISTANCE",
# # # # #             "value": (
# # # # #                 f"{float(cce.d_causal):.4f}"
# # # # #             ),
# # # # #             "explanation": (
# # # # #                 "How far the proposed state is\n"
# # # # #                 "from the observed causal state."
# # # # #             ),
# # # # #         },

# # # # #         {
# # # # #             "title": "RUNTIME",
# # # # #             "value": (
# # # # #                 f"{float(cce.runtime):.2f} s"
# # # # #             ),
# # # # #             "explanation": (
# # # # #                 "Time required to compute\n"
# # # # #                 "the explanation."
# # # # #             ),
# # # # #         },
# # # # #     ]

# # # # #     _show_metric_cards(
# # # # #         metrics
# # # # #     )

# # # # #     # ============================================================
# # # # #     # 4. COUNTERFACTUAL ACTION
# # # # #     # ============================================================

# # # # #     print(
# # # # #         "\n4. WHAT WOULD NEED TO CHANGE?"
# # # # #     )

# # # # #     _line()

# # # # #     if direct:

# # # # #         rows = []

# # # # #         for j in direct:

# # # # #             old = float(
# # # # #                 cce.x_obs[j]
# # # # #             )

# # # # #             new = float(
# # # # #                 cce.x_star[j]
# # # # #             )

# # # # #             delta = new - old

# # # # #             rows.append(
# # # # #                 [
# # # # #                     "★",
# # # # #                     names[j],
# # # # #                     f"{old:.4f}",
# # # # #                     f"{new:.4f}",
# # # # #                     f"{delta:+.4f}",
# # # # #                     _format_change(
# # # # #                         old,
# # # # #                         new,
# # # # #                     ),
# # # # #                 ]
# # # # #             )

# # # # #         _show_table(
# # # # #             rows,
# # # # #             [
# # # # #                 "",
# # # # #                 "Feature",
# # # # #                 "Current",
# # # # #                 "Required",
# # # # #                 "Δ",
# # # # #                 "Action",
# # # # #             ],
# # # # #             title="Direct causal actions",
# # # # #         )

# # # # #     else:

# # # # #         print(
# # # # #             "  No direct causal intervention "
# # # # #             "was identified."
# # # # #         )

# # # # #     # ============================================================
# # # # #     # 5. DOWNSTREAM SUMMARY
# # # # #     # ============================================================

# # # # #     print("\n5. CAUSAL PROPAGATION")
# # # # #     _line()

# # # # #     if downstream:

# # # # #         print(
# # # # #             f"  The direct intervention propagates "
# # # # #             f"through {downstream_count} downstream feature(s)."
# # # # #         )

# # # # #         print(
# # # # #             "  These are consequences of the causal "
# # # # #             "structure, not additional user actions."
# # # # #         )

# # # # #         # Only show a compact table.

# # # # #         rows = []

# # # # #         for j in downstream:

# # # # #             old = float(
# # # # #                 cce.x_obs[j]
# # # # #             )

# # # # #             new = float(
# # # # #                 cce.x_star[j]
# # # # #             )

# # # # #             rows.append(
# # # # #                 [
# # # # #                     names[j],
# # # # #                     f"{old:.4f}",
# # # # #                     f"{new:.4f}",
# # # # #                     f"{new - old:+.4f}",
# # # # #                 ]
# # # # #             )

# # # # #         _show_table(
# # # # #             rows,
# # # # #             [
# # # # #                 "Feature",
# # # # #                 "Original",
# # # # #                 "After propagation",
# # # # #                 "Change",
# # # # #             ],
# # # # #             title="Downstream causal effects",
# # # # #             figsize=(
# # # # #                 10,
# # # # #                 max(
# # # # #                     3,
# # # # #                     min(
# # # # #                         12,
# # # # #                         1.5 + 0.35 * len(rows),
# # # # #                     ),
# # # # #                 ),
# # # # #             ),
# # # # #         )

# # # # #     else:

# # # # #         print(
# # # # #             "  No downstream causal changes."
# # # # #         )

# # # # #     # ============================================================
# # # # #     # 6. TOP CAUSAL FACTORS
# # # # #     # ============================================================

# # # # #     print("\n6. TOP CAUSAL FACTORS")
# # # # #     _line()

# # # # #     top_k = min(
# # # # #         5,
# # # # #         len(order),
# # # # #     )

# # # # #     rows = []

# # # # #     for rank in range(top_k):

# # # # #         j = int(
# # # # #             order[rank]
# # # # #         )

# # # # #         effect = float(
# # # # #             cai_values[j]
# # # # #         )

# # # # #         rows.append(
# # # # #             [
# # # # #                 rank + 1,
# # # # #                 names[j],
# # # # #                 f"{effect:+.4f}",
# # # # #                 _effect_description(
# # # # #                     effect
# # # # #                 ),
# # # # #             ]
# # # # #         )

# # # # #     _show_table(
# # # # #         rows,
# # # # #         [
# # # # #             "Rank",
# # # # #             "Feature",
# # # # #             "CAI",
# # # # #             "Interpretation",
# # # # #         ],
# # # # #         title="Top causal factors",
# # # # #         figsize=(
# # # # #             10,
# # # # #             4,
# # # # #         ),
# # # # #     )

# # # # #     # ============================================================
# # # # #     # 7. FINAL CONCLUSION
# # # # #     # ============================================================

# # # # #     print("\n7. CONCLUSION")
# # # # #     _line()

# # # # #     print(
# # # # #         f"  {_direction_sentence(names[top], top_effect)}"
# # # # #     )

# # # # #     if cce.feasible:

# # # # #         print(
# # # # #             f"\n  A causal intervention changes the "
# # # # #             f"model output from "
# # # # #             f"{cce.y_fact:.4f} to "
# # # # #             f"{cce.y_achieved:.4f}."
# # # # #         )

# # # # #     else:

# # # # #         print(
# # # # #             f"\n  The requested target "
# # # # #             f"{cce.y_foil:.4f} could not be reached "
# # # # #             "under the learned causal constraints."
# # # # #         )

# # # # #     print()


# # # # # # ================================================================
# # # # # # 4. CAI VS SHAP
# # # # # # ================================================================

# # # # # def show_cai_vs_shap(
# # # # #     comparison: dict,
# # # # #     feature_names=None,
# # # # # ):
# # # # #     """
# # # # #     Display CAI vs observational SHAP-style attribution.

# # # # #     Shows:

# # # # #         1. Interpretation summary
# # # # #         2. CAI vs SHAP scatter plot
# # # # #         3. Difference plot
# # # # #         4. Existing detailed comparison table
# # # # #     """

# # # # #     if not isinstance(
# # # # #         comparison,
# # # # #         dict,
# # # # #     ):
# # # # #         raise TypeError(
# # # # #             "comparison must be a dictionary."
# # # # #         )

# # # # #     required = {
# # # # #         "cai",
# # # # #         "shap_style",
# # # # #         "baseline_int",
# # # # #         "baseline_obs",
# # # # #     }

# # # # #     missing = [
# # # # #         key
# # # # #         for key in required
# # # # #         if key not in comparison
# # # # #     ]

# # # # #     if missing:

# # # # #         raise KeyError(
# # # # #             "CAI vs SHAP comparison is missing: "
# # # # #             + ", ".join(missing)
# # # # #         )

# # # # #     cai = np.asarray(
# # # # #         comparison["cai"],
# # # # #         dtype=float,
# # # # #     )

# # # # #     shap = np.asarray(
# # # # #         comparison["shap_style"],
# # # # #         dtype=float,
# # # # #     )

# # # # #     if cai.shape != shap.shape:

# # # # #         raise ValueError(
# # # # #             "CAI and SHAP arrays must have "
# # # # #             "the same shape."
# # # # #         )

# # # # #     names = _names(
# # # # #         cai,
# # # # #         feature_names,
# # # # #     )

# # # # #     difference = (
# # # # #         cai - shap
# # # # #     )

# # # # #     bias_threshold = 0.05

# # # # #     order = np.argsort(
# # # # #         np.abs(difference)
# # # # #     )[::-1]

# # # # #     _header(
# # # # #         "CAUSAL vs OBSERVATIONAL ATTRIBUTION"
# # # # #     )

# # # # #     # ============================================================
# # # # #     # Interpretation
# # # # #     # ============================================================

# # # # #     print(
# # # # #         "\nCAI"
# # # # #     )

# # # # #     _line()

# # # # #     print(
# # # # #         "  Measures the change in expected model output "
# # # # #         "under an active feature intervention."
# # # # #     )

# # # # #     print(
# # # # #         "\nSHAP-style"
# # # # #     )

# # # # #     _line()

# # # # #     print(
# # # # #         "  Describes feature contribution using "
# # # # #         "observational relationships."
# # # # #     )

# # # # #     print(
# # # # #         "\nWhy compare them?"
# # # # #     )

# # # # #     _line()

# # # # #     print(
# # # # #         "  Large disagreement means that the feature's "
# # # # #         "observational contribution differs from its "
# # # # #         "estimated interventional causal effect."
# # # # #     )

# # # # #     # ============================================================
# # # # #     # Baselines
# # # # #     # ============================================================

# # # # #     print(
# # # # #         "\nREFERENCE OUTPUTS"
# # # # #     )

# # # # #     _line()

# # # # #     print(
# # # # #         f"  Interventional baseline : "
# # # # #         f"{comparison['baseline_int']:.4f}"
# # # # #     )

# # # # #     print(
# # # # #         f"  Observational baseline  : "
# # # # #         f"{comparison['baseline_obs']:.4f}"
# # # # #     )

# # # # #     # ============================================================
# # # # #     # Scatter plot
# # # # #     # ============================================================

# # # # #     plt = _get_plt()

# # # # #     fig, ax = plt.subplots(
# # # # #         figsize=(8, 7)
# # # # #     )

# # # # #     ax.scatter(
# # # # #         shap,
# # # # #         cai,
# # # # #         s=65,
# # # # #     )

# # # # #     minimum = min(
# # # # #         float(np.min(shap)),
# # # # #         float(np.min(cai)),
# # # # #     )

# # # # #     maximum = max(
# # # # #         float(np.max(shap)),
# # # # #         float(np.max(cai)),
# # # # #     )

# # # # #     padding = (
# # # # #         maximum - minimum
# # # # #     ) * 0.08 + 1e-6

# # # # #     ax.plot(
# # # # #         [
# # # # #             minimum - padding,
# # # # #             maximum + padding,
# # # # #         ],
# # # # #         [
# # # # #             minimum - padding,
# # # # #             maximum + padding,
# # # # #         ],
# # # # #         linestyle="--",
# # # # #         linewidth=1.5,
# # # # #     )

# # # # #     for i in range(
# # # # #         len(names)
# # # # #     ):

# # # # #         ax.annotate(
# # # # #             names[i],
# # # # #             (
# # # # #                 shap[i],
# # # # #                 cai[i],
# # # # #             ),
# # # # #             fontsize=7,
# # # # #             xytext=(4, 4),
# # # # #             textcoords="offset points",
# # # # #         )

# # # # #     ax.set_xlabel(
# # # # #         "SHAP-style attribution"
# # # # #     )

# # # # #     ax.set_ylabel(
# # # # #         "CAI"
# # # # #     )

# # # # #     ax.set_title(
# # # # #         "CAI vs SHAP-style attribution",
# # # # #         fontweight="bold",
# # # # #     )

# # # # #     ax.grid(
# # # # #         alpha=0.2
# # # # #     )

# # # # #     plt.tight_layout()
# # # # #     plt.show()

# # # # #     # ============================================================
# # # # #     # Difference chart
# # # # #     # ============================================================

# # # # #     sorted_names = [
# # # # #         names[int(j)]
# # # # #         for j in order
# # # # #     ]

# # # # #     sorted_difference = [
# # # # #         float(difference[int(j)])
# # # # #         for j in order
# # # # #     ]

# # # # #     fig, ax = plt.subplots(
# # # # #         figsize=(
# # # # #             10,
# # # # #             max(
# # # # #                 5,
# # # # #                 0.35 * len(order),
# # # # #             ),
# # # # #         )
# # # # #     )

# # # # #     y = np.arange(
# # # # #         len(order)
# # # # #     )

# # # # #     ax.barh(
# # # # #         y,
# # # # #         sorted_difference,
# # # # #     )

# # # # #     ax.axvline(
# # # # #         0,
# # # # #         linewidth=1,
# # # # #     )

# # # # #     ax.set_yticks(
# # # # #         y
# # # # #     )

# # # # #     ax.set_yticklabels(
# # # # #         sorted_names
# # # # #     )

# # # # #     ax.invert_yaxis()

# # # # #     ax.set_xlabel(
# # # # #         "CAI − SHAP-style"
# # # # #     )

# # # # #     ax.set_title(
# # # # #         "Where CAI and SHAP-style attribution disagree",
# # # # #         fontweight="bold",
# # # # #     )

# # # # #     plt.tight_layout()
# # # # #     plt.show()

# # # # #     # ============================================================
# # # # #     # Existing detailed table
# # # # #     # ============================================================

# # # # #     print(
# # # # #         "\nDETAILED COMPARISON"
# # # # #     )

# # # # #     _line()

# # # # #     rows = []

# # # # #     n_biased = 0

# # # # #     for rank, j in enumerate(order):

# # # # #         j = int(j)

# # # # #         diff = float(
# # # # #             difference[j]
# # # # #         )

# # # # #         biased = (
# # # # #             abs(diff)
# # # # #             > bias_threshold
# # # # #         )

# # # # #         if biased:
# # # # #             n_biased += 1

# # # # #         rows.append(
# # # # #             [
# # # # #                 rank + 1,
# # # # #                 names[j],
# # # # #                 f"{cai[j]:+.4f}",
# # # # #                 f"{shap[j]:+.4f}",
# # # # #                 f"{diff:+.4f}",
# # # # #                 "⚠" if biased else "✓",
# # # # #             ]
# # # # #         )

# # # # #     _show_table(
# # # # #         rows,
# # # # #         [
# # # # #             "Rank",
# # # # #             "Feature",
# # # # #             "CAI",
# # # # #             "SHAP",
# # # # #             "Difference",
# # # # #             "Flag",
# # # # #         ],
# # # # #         title="CAI vs SHAP-style comparison",
# # # # #         figsize=(
# # # # #             11,
# # # # #             max(
# # # # #                 4,
# # # # #                 min(
# # # # #                     15,
# # # # #                     1.5 + 0.35 * len(rows),
# # # # #                 ),
# # # # #             ),
# # # # #         ),
# # # # #         font_size=8,
# # # # #     )

# # # # #     print(
# # # # #         f"\n  Features with |CAI − SHAP| > "
# # # # #         f"{bias_threshold:.2f}: "
# # # # #         f"{n_biased}/{len(cai)}"
# # # # #     )

# # # # #     if len(order):

# # # # #         largest = int(
# # # # #             order[0]
# # # # #         )

# # # # #         print(
# # # # #             "\nLARGEST DISAGREEMENT"
# # # # #         )

# # # # #         _line()

# # # # #         print(
# # # # #             f"  Feature    : "
# # # # #             f"{names[largest]}"
# # # # #         )

# # # # #         print(
# # # # #             f"  CAI        : "
# # # # #             f"{cai[largest]:+.4f}"
# # # # #         )

# # # # #         print(
# # # # #             f"  SHAP       : "
# # # # #             f"{shap[largest]:+.4f}"
# # # # #         )

# # # # #         print(
# # # # #             f"  Difference : "
# # # # #             f"{difference[largest]:+.4f}"
# # # # #         )

# # # # #     print()


# # # # # # ================================================================
# # # # # # 5. FIT DISPLAY
# # # # # # ================================================================

# # # # # def show_fit(
# # # # #     model,
# # # # #     feature_names=None,
# # # # #     verbose=False,
# # # # # ):
# # # # #     """
# # # # #     Display the fitted CAUSE-XAI model.

# # # # #     Shows:

# # # # #         - model readiness
# # # # #         - causal graph
# # # # #         - causal structure summary
# # # # #         - optional ANM mechanism details
# # # # #     """

# # # # #     _header(
# # # # #         "CAUSE-XAI — MODEL READY"
# # # # #     )

# # # # #     print(
# # # # #         "\nMODEL STATUS"
# # # # #     )

# # # # #     _line()

# # # # #     print(
# # # # #         "  ✓ Causal structure discovered"
# # # # #     )

# # # # #     print(
# # # # #         "  ✓ Causal mechanisms fitted"
# # # # #     )

# # # # #     print(
# # # # #         "  ✓ Model ready for explanation"
# # # # #     )

# # # # #     # ============================================================
# # # # #     # Adjacency
# # # # #     # ============================================================

# # # # #     adj = getattr(
# # # # #         model,
# # # # #         "_adj",
# # # # #         None,
# # # # #     )

# # # # #     if adj is None:

# # # # #         adj = getattr(
# # # # #             model,
# # # # #             "adj_",
# # # # #             None,
# # # # #         )

# # # # #     if adj is None:

# # # # #         print(
# # # # #             "\n  Causal structure information "
# # # # #             "is unavailable."
# # # # #         )

# # # # #         return

# # # # #     adj = np.asarray(
# # # # #         adj
# # # # #     )

# # # # #     p = adj.shape[0]

# # # # #     names = (
# # # # #         list(feature_names)
# # # # #         if feature_names is not None
# # # # #         else [
# # # # #             f"X{i + 1}"
# # # # #             for i in range(p)
# # # # #         ]
# # # # #     )

# # # # #     edges = []

# # # # #     for i in range(p):

# # # # #         for j in range(p):

# # # # #             if adj[i, j] != 0:

# # # # #                 edges.append(
# # # # #                     (
# # # # #                         i,
# # # # #                         j,
# # # # #                     )
# # # # #                 )

# # # # #     parents = {
# # # # #         j: []
# # # # #         for j in range(p)
# # # # #     }

# # # # #     children = {
# # # # #         i: []
# # # # #         for i in range(p)
# # # # #     }

# # # # #     for i, j in edges:

# # # # #         children[i].append(j)
# # # # #         parents[j].append(i)

# # # # #     roots = [
# # # # #         names[i]
# # # # #         for i in range(p)
# # # # #         if not parents[i]
# # # # #     ]

# # # # #     sinks = [
# # # # #         names[i]
# # # # #         for i in range(p)
# # # # #         if not children[i]
# # # # #     ]

# # # # #     print(
# # # # #         "\nCAUSAL STRUCTURE"
# # # # #     )

# # # # #     _line()

# # # # #     rows = [

# # # # #         [
# # # # #             "Variables",
# # # # #             p,
# # # # #         ],

# # # # #         [
# # # # #             "Relationships discovered",
# # # # #             len(edges),
# # # # #         ],

# # # # #         [
# # # # #             "Root variables",
# # # # #             len(roots),
# # # # #         ],

# # # # #         [
# # # # #             "Sink variables",
# # # # #             len(sinks),
# # # # #         ],

# # # # #     ]

# # # # #     _show_table(
# # # # #         rows,
# # # # #         [
# # # # #             "Property",
# # # # #             "Value",
# # # # #         ],
# # # # #         title="Learned causal structure",
# # # # #         figsize=(
# # # # #             7,
# # # # #             3.5,
# # # # #         ),
# # # # #     )

# # # # #     # ============================================================
# # # # #     # DAG
# # # # #     # ============================================================

# # # # #     try:

# # # # #         dag = show_dag(
# # # # #             model,
# # # # #             feature_names=names,
# # # # #         )

# # # # #         if dag is not None:

# # # # #             try:

# # # # #                 dag.view()

# # # # #             except Exception:

# # # # #                 print(
# # # # #                     "\n  DAG object created successfully."
# # # # #                 )

# # # # #     except Exception as exc:

# # # # #         print(
# # # # #             f"\n  DAG visualization unavailable: "
# # # # #             f"{exc}"
# # # # #         )

# # # # #     # ============================================================
# # # # #     # ANM details
# # # # #     # ============================================================

# # # # #     if verbose:

# # # # #         anm = getattr(
# # # # #             model,
# # # # #             "anm_",
# # # # #             None,
# # # # #         )

# # # # #         if anm is not None:

# # # # #             print(
# # # # #                 "\nCAUSAL MECHANISM FIT"
# # # # #             )

# # # # #             _line()

# # # # #             rows = []

# # # # #             residual_std = getattr(
# # # # #                 anm,
# # # # #                 "residual_std",
# # # # #                 {},
# # # # #             )

# # # # #             noise = getattr(
# # # # #                 anm,
# # # # #                 "noise",
# # # # #                 {},
# # # # #             )

# # # # #             eqs = getattr(
# # # # #                 anm,
# # # # #                 "eqs",
# # # # #                 {},
# # # # #             )

# # # # #             for j in anm.order:

# # # # #                 variable = (
# # # # #                     names[j]
# # # # #                     if j < len(names)
# # # # #                     else f"X{j + 1}"
# # # # #                 )

# # # # #                 eq = eqs.get(
# # # # #                     j
# # # # #                 )

# # # # #                 parent_names = []

# # # # #                 if eq is not None:

# # # # #                     for parent in eq.parents:

# # # # #                         if parent < len(names):

# # # # #                             parent_names.append(
# # # # #                                 names[parent]
# # # # #                             )

# # # # #                         else:

# # # # #                             parent_names.append(
# # # # #                                 f"X{parent + 1}"
# # # # #                             )

# # # # #                 parents_text = (
# # # # #                     ", ".join(parent_names)
# # # # #                     if parent_names
# # # # #                     else "None"
# # # # #                 )

# # # # #                 noise_text = "-"

# # # # #                 if j in noise:

# # # # #                     loc, scale = noise[j]

# # # # #                     noise_text = (
# # # # #                         f"Laplace("
# # # # #                         f"loc={loc:.3f}, "
# # # # #                         f"scale={scale:.3f})"
# # # # #                     )

# # # # #                 std = residual_std.get(
# # # # #                     j,
# # # # #                     np.nan,
# # # # #                 )

# # # # #                 rows.append(
# # # # #                     [
# # # # #                         variable,
# # # # #                         parents_text,
# # # # #                         noise_text,
# # # # #                         f"{float(std):.4f}",
# # # # #                     ]
# # # # #                 )

# # # # #             _show_table(
# # # # #                 rows,
# # # # #                 [
# # # # #                     "Variable",
# # # # #                     "Parents",
# # # # #                     "Noise",
# # # # #                     "Residual std",
# # # # #                 ],
# # # # #                 title="Fitted causal mechanisms",
# # # # #                 figsize=(
# # # # #                     12,
# # # # #                     max(
# # # # #                         4,
# # # # #                         min(
# # # # #                             15,
# # # # #                             1.5 + 0.35 * len(rows),
# # # # #                         ),
# # # # #                     ),
# # # # #                 ),
# # # # #                 font_size=8,
# # # # #             )

# # # # #     print()


# # # # # # ================================================================
# # # # # # DAG DISPLAY
# # # # # # ================================================================

# # # # # def show_dag(
# # # # #     model,
# # # # #     feature_names=None,
# # # # # ):
# # # # #     """
# # # # #     Create a Graphviz representation of the learned DAG.

# # # # #     Returns
# # # # #     -------
# # # # #     graphviz.Digraph or None
# # # # #     """

# # # # #     try:

# # # # #         from graphviz import Digraph

# # # # #     except ImportError:

# # # # #         print(
# # # # #             "DAG visualization requires the Python "
# # # # #             "graphviz package."
# # # # #         )

# # # # #         print(
# # # # #             "Install with:"
# # # # #         )

# # # # #         print(
# # # # #             "    pip install graphviz"
# # # # #         )

# # # # #         return None

# # # # #     adj = np.asarray(
# # # # #         model._adj
# # # # #     )

# # # # #     p = adj.shape[0]

# # # # #     if feature_names is not None:

# # # # #         names = list(
# # # # #             feature_names
# # # # #         )

# # # # #     else:

# # # # #         names = [
# # # # #             f"X{i + 1}"
# # # # #             for i in range(p)
# # # # #         ]

# # # # #     dot = Digraph(
# # # # #         "CAUSE_XAI_DAG"
# # # # #     )

# # # # #     dot.attr(
# # # # #         rankdir="LR",
# # # # #         splines="ortho",
# # # # #         nodesep="0.45",
# # # # #         ranksep="0.8",
# # # # #         bgcolor="white",
# # # # #     )

# # # # #     dot.attr(
# # # # #         "node",
# # # # #         shape="box",
# # # # #         style="rounded",
# # # # #         fontsize="11",
# # # # #         margin="0.12",
# # # # #     )

# # # # #     dot.attr(
# # # # #         "edge",
# # # # #         arrowsize="0.7",
# # # # #         penwidth="1.2",
# # # # #     )

# # # # #     for i, name in enumerate(names):

# # # # #         has_parent = np.any(
# # # # #             adj[:, i]
# # # # #         )

# # # # #         has_child = np.any(
# # # # #             adj[i, :]
# # # # #         )

# # # # #         if not has_parent:

# # # # #             label = (
# # # # #                 f"{name}\\n(root)"
# # # # #             )

# # # # #         elif not has_child:

# # # # #             label = (
# # # # #                 f"{name}\\n(sink)"
# # # # #             )

# # # # #         else:

# # # # #             label = name

# # # # #         dot.node(
# # # # #             str(i),
# # # # #             label,
# # # # #         )

# # # # #     for i in range(p):

# # # # #         for j in range(p):

# # # # #             if adj[i, j] != 0:

# # # # #                 dot.edge(
# # # # #                     str(i),
# # # # #                     str(j),
# # # # #                 )

# # # # #     return dot


# # # # # # ================================================================
# # # # # # GENERIC DISPLAY
# # # # # # ================================================================

# # # # # def display(
# # # # #     result,
# # # # #     feature_names=None,
# # # # # ):
# # # # #     """
# # # # #     Automatically select the appropriate CAUSE-XAI display.

# # # # #     No task/classification/regression argument is required.
# # # # #     """

# # # # #     if isinstance(
# # # # #         result,
# # # # #         UnifiedExplanation,
# # # # #     ):

# # # # #         return show_explanation(
# # # # #             result,
# # # # #             feature_names=feature_names,
# # # # #         )

# # # # #     if isinstance(
# # # # #         result,
# # # # #         CCEResult,
# # # # #     ):

# # # # #         return show_counterfactual(
# # # # #             result,
# # # # #             feature_names=feature_names,
# # # # #         )

# # # # #     if isinstance(
# # # # #         result,
# # # # #         CAIResult,
# # # # #     ):

# # # # #         return show_attribution(
# # # # #             result,
# # # # #             feature_names=feature_names,
# # # # #         )

# # # # #     if isinstance(
# # # # #         result,
# # # # #         dict,
# # # # #     ):

# # # # #         if (
# # # # #             "cai" in result
# # # # #             and "shap_style" in result
# # # # #         ):

# # # # #             return show_cai_vs_shap(
# # # # #                 result,
# # # # #                 feature_names=feature_names,
# # # # #             )

# # # # #         raise TypeError(
# # # # #             "Dictionary does not contain a recognised "
# # # # #             "CAUSE-XAI result."
# # # # #         )

# # # # #     raise TypeError(
# # # # #         f"Unsupported result type: "
# # # # #         f"{type(result).__name__}"
# # # # #     )


# # # # # # ================================================================
# # # # # # PUBLIC API
# # # # # # ================================================================

# # # # # __all__ = [
# # # # #     "show_fit",
# # # # #     "show_counterfactual",
# # # # #     "show_attribution",
# # # # #     "show_explanation",
# # # # #     "show_cai_vs_shap",
# # # # #     "show_dag",
# # # # #     "display",
# # # # # ]


# # # # # # # # src/cause/display.py

# # # # # # # """
# # # # # # # User-facing display layer for CAUSE-XAI.

# # # # # # # The result classes contain the numerical results.
# # # # # # # This module converts those results into concise,
# # # # # # # human-readable explanations.

# # # # # # # Main principle:
# # # # # # #     Do not expose normalized X1/X2/... values as the
# # # # # # #     primary explanation.

# # # # # # #     Explain:
# # # # # # #         - What was predicted?
# # # # # # #         - What influenced it?
# # # # # # #         - What could change it?
# # # # # # #         - Was that change causally feasible?
# # # # # # # """

# # # # # # # 
# # # # import numpy as np

# # # # # ================================================================
# # # # # COMPACT VISUAL THEME
# # # # # ================================================================
# # # # # Presentation-only settings. Numerical/model logic is unchanged.
# # # # TOP_N = 5

# # # # THEME = {
# # # #     "primary": "#17324D",
# # # #     "secondary": "#64748B",
# # # #     "positive": "#2E7D32",
# # # #     "negative": "#C62828",
# # # #     "warning": "#B7791F",
# # # #     "grid": "#CBD5E1",
# # # #     "text": "#1F2937",
# # # #     "muted": "#64748B",
# # # # }

# # # # CHART_FIGSIZE = (7.0, 4.2)
# # # # CHART_TITLE_SIZE = 10
# # # # CHART_LABEL_SIZE = 8
# # # # CHART_TICK_SIZE = 8
# # # # CHART_ANNOTATION_SIZE = 7


# # # # # # # from .config import TARGET_PROB
# # # # # # # from .results import CCEResult, CAIResult, UnifiedExplanation


# # # # # # # # ================================================================
# # # # # # # # BASIC HELPERS
# # # # # # # # ================================================================

# # # # # # # def _names(values, feature_names=None):
# # # # # # #     """Return readable feature names."""

# # # # # # #     n = len(values)

# # # # # # #     if feature_names is not None:
# # # # # # #         if len(feature_names) != n:
# # # # # # #             raise ValueError(
# # # # # # #                 "feature_names must have the same length as the features."
# # # # # # #             )

# # # # # # #         return list(feature_names)

# # # # # # #     return [f"Feature {i + 1}" for i in range(n)]


# # # # # # # def _line(char="─", width=78):
# # # # # # #     print(char * width)


# # # # # # # def _header(title, width=78):
# # # # # # #     print()
# # # # # # #     print("═" * width)
# # # # # # #     print(title.center(width))
# # # # # # #     print("═" * width)


# # # # # # # def _format_change(old, new):
# # # # # # #     """
# # # # # # #     Convert a numerical change into readable language.
# # # # # # #     """

# # # # # # #     delta = float(new) - float(old)

# # # # # # #     if abs(delta) < 1e-10:
# # # # # # #         return "no change"

# # # # # # #     if delta > 0:
# # # # # # #         return f"increase by {abs(delta):.3f}"

# # # # # # #     return f"decrease by {abs(delta):.3f}"


# # # # # # # def _effect_description(effect):
# # # # # # #     """
# # # # # # #     Generate varied human-readable descriptions.

# # # # # # #     Avoids repeating:
# # # # # # #         'pushes the prediction higher/lower'
# # # # # # #     """

# # # # # # #     effect = float(effect)

# # # # # # #     if abs(effect) < 1e-10:
# # # # # # #         return "Little measurable influence"

# # # # # # #     magnitude = abs(effect)

# # # # # # #     if effect > 0:

# # # # # # #         if magnitude >= 20:
# # # # # # #             return "Strong upward influence"

# # # # # # #         if magnitude >= 10:
# # # # # # #             return "Moderate upward influence"

# # # # # # #         return "Slight upward influence"

# # # # # # #     else:

# # # # # # #         if magnitude >= 20:
# # # # # # #             return "Strong downward influence"

# # # # # # #         if magnitude >= 10:
# # # # # # #             return "Moderate downward influence"

# # # # # # #         return "Slight downward influence"


# # # # # # # def _direction_sentence(feature, effect):
# # # # # # #     """
# # # # # # #     Create one natural sentence for the strongest driver.
# # # # # # #     """

# # # # # # #     effect = float(effect)

# # # # # # #     if effect > 0:
# # # # # # #         return (
# # # # # # #             f"{feature} is the strongest factor increasing "
# # # # # # #             f"the predicted outcome."
# # # # # # #         )

# # # # # # #     if effect < 0:
# # # # # # #         return (
# # # # # # #             f"{feature} is the strongest factor decreasing "
# # # # # # #             f"the predicted outcome."
# # # # # # #         )

# # # # # # #     return (
# # # # # # #         f"{feature} has little measurable influence "
# # # # # # #         f"on the predicted outcome."
# # # # # # #     )


# # # # # # # # ================================================================
# # # # # # # # CAUSAL IMPACT TABLE
# # # # # # # # ================================================================

# # # # # # # def _feature_table(cai, names):

# # # # # # #     cai = np.asarray(cai, dtype=float)

# # # # # # #     order = np.argsort(np.abs(cai))[::-1]

# # # # # # #     print(
# # # # # # #         f"{'Feature':<20}"
# # # # # # #         f"{'Causal effect':>17}"
# # # # # # #         f"{'Interpretation':>35}"
# # # # # # #     )

# # # # # # #     _line()

# # # # # # #     for j in order:

# # # # # # #         effect = float(cai[j])

# # # # # # #         print(
# # # # # # #             f"{names[j]:<20}"
# # # # # # #             f"{effect:>+17.3f}"
# # # # # # #             f"{_effect_description(effect):>35}"
# # # # # # #         )


# # # # # # # # ================================================================
# # # # # # # # 1. COUNTERFACTUAL
# # # # # # # # ================================================================

# # # # # # # def show_counterfactual(
# # # # # # #     result: CCEResult,
# # # # # # #     feature_names=None,
# # # # # # #     task="regression",
# # # # # # # ):
# # # # # # #     """
# # # # # # #     Display the counterfactual result.

# # # # # # #     Answers:
# # # # # # #         WHAT WOULD NEED TO CHANGE?
# # # # # # #     """

# # # # # # #     names = _names(result.x_obs, feature_names)

# # # # # # #     _header("COUNTERFACTUAL EXPLANATION")

# # # # # # #     # ------------------------------------------------------------
# # # # # # #     # Prediction
# # # # # # #     # ------------------------------------------------------------

# # # # # # #     print("\nCurrent prediction")
# # # # # # #     _line()

# # # # # # #     print(f"  {result.y_fact:.3f}")

# # # # # # #     print("\nRequested target")
# # # # # # #     _line()

# # # # # # #     print(f"  {result.y_foil:.3f}")

# # # # # # #     print("\nOutcome")
# # # # # # #     _line()

# # # # # # #     if result.feasible:

# # # # # # #         print("  Target reached : YES")

# # # # # # #         print(
# # # # # # #             f"  Prediction     : "
# # # # # # #             f"{result.y_fact:.3f} → "
# # # # # # #             f"{result.y_achieved:.3f}"
# # # # # # #         )

# # # # # # #     else:

# # # # # # #         print("  Target reached : NO")

# # # # # # #         print(
# # # # # # #             f"  Best prediction found : "
# # # # # # #             f"{result.y_achieved:.3f}"
# # # # # # #         )

# # # # # # #     # ------------------------------------------------------------
# # # # # # #     # What needs to change?
# # # # # # #     # ------------------------------------------------------------

# # # # # # #     print("\nWhat would need to change?")
# # # # # # #     _line()

# # # # # # #     direct = result.direct_interventions or []

# # # # # # #     if result.feasible and direct:

# # # # # # #         for j in direct:

# # # # # # #             old = float(result.x_obs[j])
# # # # # # #             new = float(result.x_star[j])

# # # # # # #             print(f"\n  {names[j]}")
# # # # # # #             print(f"    Current value : {old:.3f}")
# # # # # # #             print(f"    New value     : {new:.3f}")
# # # # # # #             print(
# # # # # # #                 f"    Required     : "
# # # # # # #                 f"{_format_change(old, new)}"
# # # # # # #             )

# # # # # # #     elif result.feasible and result.changed:

# # # # # # #         for j in result.changed:

# # # # # # #             old = float(result.x_obs[j])
# # # # # # #             new = float(result.x_star[j])

# # # # # # #             print(f"\n  {names[j]}")
# # # # # # #             print(f"    Current value : {old:.3f}")
# # # # # # #             print(f"    New value     : {new:.3f}")
# # # # # # #             print(
# # # # # # #                 f"    Required     : "
# # # # # # #                 f"{_format_change(old, new)}"
# # # # # # #             )

# # # # # # #     else:

# # # # # # #         print(
# # # # # # #             "  No feasible feature change was found "
# # # # # # #             "under the current causal constraints."
# # # # # # #         )

# # # # # # #     # ------------------------------------------------------------
# # # # # # #     # Validity
# # # # # # #     # ------------------------------------------------------------

# # # # # # #     print("\nCausal validity")
# # # # # # #     _line()

# # # # # # #     if result.violation < 1.5:

# # # # # # #         print(
# # # # # # #             "  ✓ The resulting state is consistent with "
# # # # # # #             "the learned causal structure."
# # # # # # #         )

# # # # # # #     else:

# # # # # # #         print(
# # # # # # #             "  ⚠ The resulting state may be inconsistent "
# # # # # # #             "with the learned causal structure."
# # # # # # #         )

# # # # # # #     print(f"\n  Causal distance : {result.d_causal:.3f}")
# # # # # # #     print(f"  Causal sparsity : {result.sparsity:.2f}")
# # # # # # #     print(f"  Runtime         : {result.runtime:.3f} sec")


# # # # # # # # ================================================================
# # # # # # # # 2. CAUSAL FEATURE IMPACT
# # # # # # # # ================================================================

# # # # # # # def show_attribution(
# # # # # # #     result: CAIResult,
# # # # # # #     feature_names=None,
# # # # # # #     task="regression",
# # # # # # # ):
# # # # # # #     """
# # # # # # #     Display causal feature impact.

# # # # # # #     Answers:
# # # # # # #         WHICH FEATURES MATTER?
# # # # # # #     """

# # # # # # #     names = _names(result.x_obs, feature_names)

# # # # # # #     cai = np.asarray(result.cai, dtype=float)

# # # # # # #     _header("CAUSAL FEATURE IMPACT")

# # # # # # #     print(
# # # # # # #         "\nThe causal effect estimates how actively changing "
# # # # # # #         "each feature influences the model output."
# # # # # # #     )

# # # # # # #     print()

# # # # # # #     _feature_table(cai, names)

# # # # # # #     # ------------------------------------------------------------
# # # # # # #     # Main driver
# # # # # # #     # ------------------------------------------------------------

# # # # # # #     order = np.argsort(np.abs(cai))[::-1]

# # # # # # #     top = int(order[0])
# # # # # # #     top_effect = float(cai[top])

# # # # # # #     print("\nMain causal driver")
# # # # # # #     _line()

# # # # # # #     print(
# # # # # # #         f"  {_direction_sentence(names[top], top_effect)}"
# # # # # # #     )

# # # # # # #     print(
# # # # # # #         f"  Estimated effect : {top_effect:+.3f}"
# # # # # # #     )

# # # # # # #     # ------------------------------------------------------------
# # # # # # #     # Reading guide
# # # # # # #     # ------------------------------------------------------------

# # # # # # #     print("\nHow to read this")
# # # # # # #     _line()

# # # # # # #     print(
# # # # # # #         "  Positive → the intervention moves the outcome upward."
# # # # # # #     )

# # # # # # #     print(
# # # # # # #         "  Negative → the intervention moves the outcome downward."
# # # # # # #     )

# # # # # # #     print(
# # # # # # #         "  Larger absolute value → stronger estimated effect."
# # # # # # #     )


# # # # # # # # ================================================================
# # # # # # # # 3. UNIFIED EXPLANATION
# # # # # # # # ================================================================

# # # # # # # def show_explanation(
# # # # # # #     explanation: UnifiedExplanation,
# # # # # # #     feature_names=None,
# # # # # # #     task="regression",
# # # # # # # ):
# # # # # # #     """
# # # # # # #     Main CAUSE-XAI user-facing explanation.

# # # # # # #     IMPORTANT:
# # # # # # #         This intentionally does NOT call:
# # # # # # #             show_counterfactual()
# # # # # # #             show_attribution()

# # # # # # #         because doing so would duplicate information.

# # # # # # #     Instead, it creates one compact explanation containing:

# # # # # # #         1. Prediction
# # # # # # #         2. Main reasons
# # # # # # #         3. Counterfactual action
# # # # # # #         4. Causal validity
# # # # # # #         5. Plain-language conclusion
# # # # # # #     """

# # # # # # #     names = _names(
# # # # # # #         explanation.x_obs,
# # # # # # #         feature_names
# # # # # # #     )

# # # # # # #     cce = explanation.cce
# # # # # # #     cai = explanation.cai

# # # # # # #     cai_values = np.asarray(
# # # # # # #         cai.cai,
# # # # # # #         dtype=float
# # # # # # #     )

# # # # # # #     order = np.argsort(
# # # # # # #         np.abs(cai_values)
# # # # # # #     )[::-1]

# # # # # # #     _header("CAUSE-XAI — MODEL EXPLANATION")

# # # # # # #     # ============================================================
# # # # # # #     # 1. PREDICTION
# # # # # # #     # ============================================================

# # # # # # #     print("\n1. PREDICTION")
# # # # # # #     _line()

# # # # # # #     print(
# # # # # # #         f"  Current prediction : "
# # # # # # #         f"{explanation.y_fact:.3f}"
# # # # # # #     )

# # # # # # #     if task == "regression":

# # # # # # #         print(
# # # # # # #             f"  Requested target  : "
# # # # # # #             f"{explanation.y_foil:.3f}"
# # # # # # #         )

# # # # # # #         print(
# # # # # # #             f"  Result             : "
# # # # # # #             f"{cce.y_achieved:.3f}"
# # # # # # #         )

# # # # # # #     else:

# # # # # # #         factual_class = int(
# # # # # # #             explanation.y_fact >= TARGET_PROB
# # # # # # #         )

# # # # # # #         achieved_class = int(
# # # # # # #             cce.y_achieved >= TARGET_PROB
# # # # # # #         )

# # # # # # #         print(
# # # # # # #             f"  Current class     : "
# # # # # # #             f"{factual_class}"
# # # # # # #         )

# # # # # # #         print(
# # # # # # #             f"  Desired class     : "
# # # # # # #             f"{int(explanation.y_foil)}"
# # # # # # #         )

# # # # # # #         print(
# # # # # # #             f"  Achieved class    : "
# # # # # # #             f"{achieved_class}"
# # # # # # #         )

# # # # # # #     # ============================================================
# # # # # # #     # 2. MAIN FACTORS
# # # # # # #     # ============================================================

# # # # # # #     print("\n2. MAIN FACTORS")
# # # # # # #     _line()

# # # # # # #     top_k = min(3, len(order))

# # # # # # #     for rank in range(top_k):

# # # # # # #         j = int(order[rank])
# # # # # # #         effect = float(cai_values[j])

# # # # # # #         description = _effect_description(effect)

# # # # # # #         print(
# # # # # # #             f"  {rank + 1}. "
# # # # # # #             f"{names[j]:<15} "
# # # # # # #             f"{effect:+.3f}   "
# # # # # # #             f"{description}"
# # # # # # #         )

# # # # # # #     # ============================================================
# # # # # # #     # 3. WHAT WOULD CHANGE THE RESULT?
# # # # # # #     # ============================================================

# # # # # # #     print("\n3. COUNTERFACTUAL — WHAT WOULD NEED TO CHANGE?")
# # # # # # #     _line()

# # # # # # #     direct = cce.direct_interventions or []

# # # # # # #     if cce.feasible:

# # # # # # #         if direct:

# # # # # # #             for j in direct:

# # # # # # #                 old = float(cce.x_obs[j])
# # # # # # #                 new = float(cce.x_star[j])

# # # # # # #                 print(f"\n  {names[j]}")

# # # # # # #                 print(
# # # # # # #                     f"    Current : {old:.3f}"
# # # # # # #                 )

# # # # # # #                 print(
# # # # # # #                     f"    Desired : {new:.3f}"
# # # # # # #                 )

# # # # # # #                 print(
# # # # # # #                     f"    Action  : "
# # # # # # #                     f"{_format_change(old, new)}"
# # # # # # #                 )

# # # # # # #         elif cce.changed:

# # # # # # #             for j in cce.changed:

# # # # # # #                 old = float(cce.x_obs[j])
# # # # # # #                 new = float(cce.x_star[j])

# # # # # # #                 print(f"\n  {names[j]}")

# # # # # # #                 print(
# # # # # # #                     f"    Current : {old:.3f}"
# # # # # # #                 )

# # # # # # #                 print(
# # # # # # #                     f"    Desired : {new:.3f}"
# # # # # # #                 )

# # # # # # #                 print(
# # # # # # #                     f"    Action  : "
# # # # # # #                     f"{_format_change(old, new)}"
# # # # # # #                 )

# # # # # # #         else:

# # # # # # #             print(
# # # # # # #                 "  No observable feature change was required."
# # # # # # #             )

# # # # # # #     else:

# # # # # # #         print(
# # # # # # #             "  No feasible change was found that reaches "
# # # # # # #             f"the requested target of {cce.y_foil:.3f}."
# # # # # # #         )

# # # # # # #         print(
# # # # # # #             "  The target is not reachable under the "
# # # # # # #             "current causal constraints."
# # # # # # #         )

# # # # # # #     # ============================================================
# # # # # # #     # 4. CAUSAL VALIDITY
# # # # # # #     # ============================================================

# # # # # # #     print("\n4. CAUSAL VALIDITY")
# # # # # # #     _line()

# # # # # # #     if cce.violation < 1.5:

# # # # # # #         print(
# # # # # # #             "  ✓ The counterfactual remains consistent "
# # # # # # #             "with the learned causal structure."
# # # # # # #         )

# # # # # # #     else:

# # # # # # #         print(
# # # # # # #             "  ⚠ The counterfactual may violate "
# # # # # # #             "the learned causal structure."
# # # # # # #         )

# # # # # # #     # ============================================================
# # # # # # #     # 5. PLAIN LANGUAGE SUMMARY
# # # # # # #     # ============================================================

# # # # # # #     print("\n5. PLAIN-LANGUAGE SUMMARY")
# # # # # # #     _line()

# # # # # # #     top = int(order[0])
# # # # # # #     top_effect = float(cai_values[top])

# # # # # # #     print(
# # # # # # #         f"  {_direction_sentence(names[top], top_effect)}"
# # # # # # #     )

# # # # # # #     if cce.feasible:

# # # # # # #         print(
# # # # # # #             f"  A feasible causal change can move the "
# # # # # # #             f"prediction from {cce.y_fact:.3f} "
# # # # # # #             f"to {cce.y_achieved:.3f}."
# # # # # # #         )

# # # # # # #     else:

# # # # # # #         print(
# # # # # # #             f"  The requested target of {cce.y_foil:.3f} "
# # # # # # #             f"could not be reached with the allowed "
# # # # # # #             f"causal interventions."
# # # # # # #         )

# # # # # # #     print()


# # # # # # # # ================================================================
# # # # # # # # 4. CAI VS SHAP
# # # # # # # # ================================================================

# # # # # # # def show_cai_vs_shap(
# # # # # # #     comparison: dict,
# # # # # # #     feature_names=None,
# # # # # # # ):
# # # # # # #     """
# # # # # # #     Technical comparison between CAI and SHAP-style attribution.

# # # # # # #     Kept separate from the main user explanation.
# # # # # # #     """

# # # # # # #     cai = np.asarray(
# # # # # # #         comparison["cai"],
# # # # # # #         dtype=float
# # # # # # #     )

# # # # # # #     shap = np.asarray(
# # # # # # #         comparison["shap_style"],
# # # # # # #         dtype=float
# # # # # # #     )

# # # # # # #     names = _names(
# # # # # # #         cai,
# # # # # # #         feature_names
# # # # # # #     )

# # # # # # #     difference = cai - shap

# # # # # # #     order = np.argsort(
# # # # # # #         np.abs(difference)
# # # # # # #     )[::-1]

# # # # # # #     _header(
# # # # # # #         "CAUSAL vs OBSERVATIONAL ATTRIBUTION"
# # # # # # #     )

# # # # # # #     print(
# # # # # # #         "\nCAI:"
# # # # # # #     )

# # # # # # #     print(
# # # # # # #         "  Estimates the effect of actively intervening "
# # # # # # #         "on a feature."
# # # # # # #     )

# # # # # # #     print(
# # # # # # #         "\nSHAP-style:"
# # # # # # #     )

# # # # # # #     print(
# # # # # # #         "  Describes the feature's contribution based "
# # # # # # #         "on observed relationships."
# # # # # # #     )

# # # # # # #     print()

# # # # # # #     print(
# # # # # # #         f"{'Feature':<20}"
# # # # # # #         f"{'CAI':>12}"
# # # # # # #         f"{'SHAP':>12}"
# # # # # # #         f"{'Difference':>15}"
# # # # # # #     )

# # # # # # #     _line()

# # # # # # #     for j in order:

# # # # # # #         print(
# # # # # # #             f"{names[j]:<20}"
# # # # # # #             f"{cai[j]:>+12.3f}"
# # # # # # #             f"{shap[j]:>+12.3f}"
# # # # # # #             f"{difference[j]:>+15.3f}"
# # # # # # #         )

# # # # # # #     print("\nLargest disagreement")
# # # # # # #     _line()

# # # # # # #     largest = int(order[0])

# # # # # # #     print(
# # # # # # #         f"  Feature : {names[largest]}"
# # # # # # #     )

# # # # # # #     print(
# # # # # # #         f"  CAI     : {cai[largest]:+.3f}"
# # # # # # #     )

# # # # # # #     print(
# # # # # # #         f"  SHAP    : {shap[largest]:+.3f}"
# # # # # # #     )


# # # # # # # # ================================================================
# # # # # # # # 5. FIT DISPLAY
# # # # # # # # ================================================================

# # # # # # # def show_fit(
# # # # # # #     model,
# # # # # # #     feature_names=None,
# # # # # # #     verbose=True,
# # # # # # # ):
# # # # # # #     """
# # # # # # #     Compact user-facing fit result.

# # # # # # #     Does not print every HSIC pair or every internal ANM value.
# # # # # # #     Those belong to diagnostic/debug output.
# # # # # # #     """

# # # # # # #     _header("CAUSE-XAI — MODEL READY")

# # # # # # #     print("\nModel status")
# # # # # # #     _line()

# # # # # # #     print(
# # # # # # #         "  ✓ Causal structure discovered"
# # # # # # #     )

# # # # # # #     print(
# # # # # # #         "  ✓ Causal mechanisms fitted"
# # # # # # #     )

# # # # # # #     print(
# # # # # # #         "  ✓ Model ready for explanation"
# # # # # # #     )

# # # # # # #     dag = getattr(
# # # # # # #         model,
# # # # # # #         "dag_",
# # # # # # #         None
# # # # # # #     )

# # # # # # #     if dag is None:

# # # # # # #         dag = getattr(
# # # # # # #             model,
# # # # # # #             "dag",
# # # # # # #             None
# # # # # # #         )

# # # # # # #     if dag is not None:

# # # # # # #         try:

# # # # # # #             edges = list(
# # # # # # #                 dag.edges()
# # # # # # #             )

# # # # # # #             print("\nCausal structure")
# # # # # # #             _line()

# # # # # # #             if feature_names is not None:

# # # # # # #                 print(
# # # # # # #                     f"  Variables : "
# # # # # # #                     f"{len(feature_names)}"
# # # # # # #                 )

# # # # # # #             else:

# # # # # # #                 print(
# # # # # # #                     f"  Variables : "
# # # # # # #                     f"{len(dag.nodes)}"
# # # # # # #                 )

# # # # # # #             print(
# # # # # # #                 f"  Relationships discovered : "
# # # # # # #                 f"{len(edges)}"
# # # # # # #             )

# # # # # # #         except Exception:
# # # # # # #             pass

# # # # # # #     print()


# # # # # # # # ================================================================
# # # # # # # # 6. GENERIC DISPLAY
# # # # # # # # ================================================================

# # # # # # # def display(
# # # # # # #     result,
# # # # # # #     feature_names=None,
# # # # # # #     task="regression",
# # # # # # # ):
# # # # # # #     """
# # # # # # #     Automatically select the appropriate display.
# # # # # # #     """

# # # # # # #     if isinstance(
# # # # # # #         result,
# # # # # # #         UnifiedExplanation
# # # # # # #     ):

# # # # # # #         show_explanation(
# # # # # # #             result,
# # # # # # #             feature_names=feature_names,
# # # # # # #             task=task,
# # # # # # #         )

# # # # # # #     elif isinstance(
# # # # # # #         result,
# # # # # # #         CCEResult
# # # # # # #     ):

# # # # # # #         show_counterfactual(
# # # # # # #             result,
# # # # # # #             feature_names=feature_names,
# # # # # # #             task=task,
# # # # # # #         )

# # # # # # #     elif isinstance(
# # # # # # #         result,
# # # # # # #         CAIResult
# # # # # # #     ):

# # # # # # #         show_attribution(
# # # # # # #             result,
# # # # # # #             feature_names=feature_names,
# # # # # # #             task=task,
# # # # # # #         )

# # # # # # #     elif isinstance(result, dict):

# # # # # # #         if (
# # # # # # #             "cai" in result
# # # # # # #             and "shap_style" in result
# # # # # # #         ):

# # # # # # #             show_cai_vs_shap(
# # # # # # #                 result,
# # # # # # #                 feature_names=feature_names,
# # # # # # #             )

# # # # # # #         else:

# # # # # # #             raise TypeError(
# # # # # # #                 "Dictionary does not contain a recognised "
# # # # # # #                 "CAUSE-XAI result."
# # # # # # #             )

# # # # # # #     else:

# # # # # # #         raise TypeError(
# # # # # # #             f"Unsupported result type: "
# # # # # # #             f"{type(result).__name__}"
# # # # # # #         )


# # # # # # # __all__ = [
# # # # # # #     "show_fit",
# # # # # # #     "show_counterfactual",
# # # # # # #     "show_attribution",
# # # # # # #     "show_explanation",
# # # # # # #     "show_cai_vs_shap",
# # # # # # #     "display",
# # # # # # # ]


# # # # # # # src/cause/display.py

# # # # # # """
# # # # # # User-facing display layer for CAUSE-XAI.

# # # # # # The result classes contain the numerical results.
# # # # # # This module converts those results into concise,
# # # # # # human-readable explanations.

# # # # # # Main principle:
# # # # # #     Do not expose normalized X1/X2/... values as the
# # # # # #     primary explanation.

# # # # # #     Explain:
# # # # # #         - What was predicted?
# # # # # #         - What influenced it?
# # # # # #         - What could change it?
# # # # # #         - Was that change causally feasible?
# # # # # # """

# # # # # # import numpy as np

# # # # # # from .config import TARGET_PROB
# # # # # # from .results import CCEResult, CAIResult, UnifiedExplanation
# # # # # # from graphviz import Digraph

# # # # # # # ================================================================
# # # # # # # BASIC HELPERS
# # # # # # # ================================================================


# # # # # # def _names(values, feature_names=None):
# # # # # #     """Return readable feature names."""
# # # # # #     n = len(values)

# # # # # #     if feature_names is not None:
# # # # # #         if len(feature_names) != n:
# # # # # #             raise ValueError(
# # # # # #                 "feature_names must have the same length as the features."
# # # # # #             )
# # # # # #         return list(feature_names)

# # # # # #     return [f"Feature {i + 1}" for i in range(n)]


# # # # # # def _line(char="─", width=78):
# # # # # #     print(char * width)


# # # # # # def _header(title, width=78):
# # # # # #     print()
# # # # # #     print("═" * width)
# # # # # #     print(title.center(width))
# # # # # #     print("═" * width)


# # # # # # def _format_change(old, new):
# # # # # #     """
# # # # # #     Convert a numerical change into readable language.
# # # # # #     """
# # # # # #     delta = float(new) - float(old)
# # # # # #     if abs(delta) < 1e-10:
# # # # # #         return "no change"
# # # # # #     if delta > 0:
# # # # # #         return f"increase by {abs(delta):.3f}"
# # # # # #     return f"decrease by {abs(delta):.3f}"


# # # # # # def _effect_description(effect):
# # # # # #     """
# # # # # #     Generate varied human-readable descriptions.
# # # # # #     """
# # # # # #     effect = float(effect)

# # # # # #     if abs(effect) < 1e-10:
# # # # # #         return "Little measurable influence"

# # # # # #     magnitude = abs(effect)

# # # # # #     if effect > 0:
# # # # # #         if magnitude >= 20:
# # # # # #             return "Strong upward influence"
# # # # # #         if magnitude >= 10:
# # # # # #             return "Moderate upward influence"
# # # # # #         return "Slight upward influence"
# # # # # #     else:
# # # # # #         if magnitude >= 20:
# # # # # #             return "Strong downward influence"
# # # # # #         if magnitude >= 10:
# # # # # #             return "Moderate downward influence"
# # # # # #         return "Slight downward influence"


# # # # # # def _direction_sentence(feature, effect):
# # # # # #     """
# # # # # #     Create one natural sentence for the strongest driver.
# # # # # #     """
# # # # # #     effect = float(effect)

# # # # # #     if effect > 0:
# # # # # #         return (
# # # # # #             f"{feature} is the strongest factor increasing "
# # # # # #             f"the predicted outcome."
# # # # # #         )
# # # # # #     if effect < 0:
# # # # # #         return (
# # # # # #             f"{feature} is the strongest factor decreasing "
# # # # # #             f"the predicted outcome."
# # # # # #         )
# # # # # #     return (
# # # # # #         f"{feature} has little measurable influence "
# # # # # #         f"on the predicted outcome."
# # # # # #     )


# # # # # # # ================================================================
# # # # # # # CAUSAL IMPACT TABLE
# # # # # # # ================================================================


# # # # # # def _feature_table(cai, names):
# # # # # #     """
# # # # # #     Print a well-aligned table of causal effects.
# # # # # #     """
# # # # # #     cai = np.asarray(cai, dtype=float)
# # # # # #     order = np.argsort(np.abs(cai))[::-1]

# # # # # #     feat_width = 20
# # # # # #     effect_width = 15
# # # # # #     interp_width = 38

# # # # # #     header = (
# # # # # #         f"{'Feature':<{feat_width}}"
# # # # # #         f"{'Causal effect':>{effect_width}}"
# # # # # #         f"{'Interpretation':>{interp_width}}"
# # # # # #     )
# # # # # #     print(header)
# # # # # #     _line(width=feat_width + effect_width + interp_width)

# # # # # #     for j in order:
# # # # # #         effect = float(cai[j])
# # # # # #         row = (
# # # # # #             f"{names[j]:<{feat_width}}"
# # # # # #             f"{effect:>{effect_width}.3f}"
# # # # # #             f"{_effect_description(effect):>{interp_width}}"
# # # # # #         )
# # # # # #         print(row)


# # # # # # # ================================================================
# # # # # # # 1. COUNTERFACTUAL
# # # # # # # ================================================================


# # # # # # # def show_counterfactual(
# # # # # # #     result: CCEResult,
# # # # # # #     feature_names=None,
# # # # # # #     task="regression",
# # # # # # # ):
# # # # # # #     """
# # # # # # #     Display the counterfactual result.

# # # # # # #     Answers:
# # # # # # #         WHAT WOULD NEED TO CHANGE?
# # # # # # #     """

# # # # # # #     names = _names(result.x_obs, feature_names)

# # # # # # #     _header("COUNTERFACTUAL EXPLANATION")

# # # # # # #     # ------------------------------------------------------------
# # # # # # #     # Prediction
# # # # # # #     # ------------------------------------------------------------
# # # # # # #     print("\nCurrent prediction")
# # # # # # #     _line()
# # # # # # #     print(f"  {result.y_fact:.3f}")

# # # # # # #     print("\nRequested target")
# # # # # # #     _line()
# # # # # # #     print(f"  {result.y_foil:.3f}")

# # # # # # #     print("\nOutcome")
# # # # # # #     _line()
# # # # # # #     if result.feasible:
# # # # # # #         print("  Target reached : YES")
# # # # # # #         print(
# # # # # # #             f"  Prediction     : "
# # # # # # #             f"{result.y_fact:.3f} → "
# # # # # # #             f"{result.y_achieved:.3f}"
# # # # # # #         )
# # # # # # #     else:
# # # # # # #         print("  Target reached : NO")
# # # # # # #         print(
# # # # # # #             f"  Best prediction found : "
# # # # # # #             f"{result.y_achieved:.3f}"
# # # # # # #         )

# # # # # # #     # ------------------------------------------------------------
# # # # # # #     # What needs to change?
# # # # # # #     # ------------------------------------------------------------
# # # # # # #     print("\nWhat would need to change?")
# # # # # # #     _line()

# # # # # # #     direct = result.direct_interventions or []

# # # # # # #     if result.feasible and direct:
# # # # # # #         for j in direct:
# # # # # # #             old = float(result.x_obs[j])
# # # # # # #             new = float(result.x_star[j])

# # # # # # #             print(f"\n  {names[j]}")
# # # # # # #             print(f"    Current value : {old:.3f}")
# # # # # # #             print(f"    New value     : {new:.3f}")
# # # # # # #             print(
# # # # # # #                 f"    Required     : "
# # # # # # #                 f"{_format_change(old, new)}"
# # # # # # #             )

# # # # # # #     elif result.feasible and result.changed:
# # # # # # #         for j in result.changed:
# # # # # # #             old = float(result.x_obs[j])
# # # # # # #             new = float(result.x_star[j])

# # # # # # #             print(f"\n  {names[j]}")
# # # # # # #             print(f"    Current value : {old:.3f}")
# # # # # # #             print(f"    New value     : {new:.3f}")
# # # # # # #             print(
# # # # # # #                 f"    Required     : "
# # # # # # #                 f"{_format_change(old, new)}"
# # # # # # #             )

# # # # # # #     else:
# # # # # # #         print(
# # # # # # #             "  No feasible feature change was found "
# # # # # # #             "under the current causal constraints."
# # # # # # #         )

# # # # # # #     # ------------------------------------------------------------
# # # # # # #     # Validity
# # # # # # #     # ------------------------------------------------------------
# # # # # # #     print("\nCausal validity")
# # # # # # #     _line()
# # # # # # #     if result.violation < 1.5:
# # # # # # #         print(
# # # # # # #             "  ✓ The resulting state is consistent with "
# # # # # # #             "the learned causal structure."
# # # # # # #         )
# # # # # # #     else:
# # # # # # #         print(
# # # # # # #             "  ⚠ The resulting state may be inconsistent "
# # # # # # #             "with the learned causal structure."
# # # # # # #         )

# # # # # # #     print(f"\n  Causal distance : {result.d_causal:.3f}")
# # # # # # #     print(f"  Causal sparsity : {result.sparsity:.2f}")
# # # # # # #     print(f"  Runtime         : {result.runtime:.3f} sec")


# # # # # # def show_counterfactual(
# # # # # #     result: CCEResult,
# # # # # #     feature_names=None,
# # # # # #     task="regression",
# # # # # # ):
# # # # # #     """
# # # # # #     Display a concise causal counterfactual explanation.

# # # # # #     Separates:
# # # # # #         1. Direct changes — features intentionally changed by CCE.
# # # # # #         2. Downstream causal changes — features changed as a
# # # # # #            consequence of the learned causal structure.
# # # # # #     """

# # # # # #     names = _names(result.x_obs, feature_names)

# # # # # #     _header("COUNTERFACTUAL EXPLANATION")

# # # # # #     # ============================================================
# # # # # #     # Prediction
# # # # # #     # ============================================================
# # # # # #     print("\nPrediction")
# # # # # #     _line()

# # # # # #     print(
# # # # # #         f"  Current prediction : "
# # # # # #         f"{result.y_fact:.3f}"
# # # # # #     )

# # # # # #     print(
# # # # # #         f"  Target prediction  : "
# # # # # #         f"{result.y_foil:.3f}"
# # # # # #     )

# # # # # #     print(
# # # # # #         f"  Achieved prediction: "
# # # # # #         f"{result.y_achieved:.3f}"
# # # # # #     )

# # # # # #     print(
# # # # # #         f"  Target reached     : "
# # # # # #         f"{'YES' if result.feasible else 'NO'}"
# # # # # #     )

# # # # # #     # ============================================================
# # # # # #     # Direct changes
# # # # # #     # ============================================================
# # # # # #     direct = result.direct_interventions or []

# # # # # #     print("\nDirect changes")
# # # # # #     _line()

# # # # # #     if direct:

# # # # # #         print(
# # # # # #             f"  {'Feature':<18}"
# # # # # #             f"{'Current':>12}"
# # # # # #             f"{'Desired':>12}"
# # # # # #             f"{'Action':>22}"
# # # # # #         )

# # # # # #         print(
# # # # # #             "  "
# # # # # #             + "─" * 64
# # # # # #         )

# # # # # #         for j in direct:

# # # # # #             old = float(result.x_obs[j])
# # # # # #             new = float(result.x_star[j])
# # # # # #             delta = new - old

# # # # # #             action = _format_change(
# # # # # #                 old,
# # # # # #                 new,
# # # # # #             )

# # # # # #             print(
# # # # # #                 f"  {names[j]:<18}"
# # # # # #                 f"{old:>12.3f}"
# # # # # #                 f"{new:>12.3f}"
# # # # # #                 f"{action:>22}"
# # # # # #             )

# # # # # #     else:

# # # # # #         print("  None")

# # # # # #     # ============================================================
# # # # # #     # Downstream causal changes
# # # # # #     # ============================================================
# # # # # #     downstream = [
# # # # # #         j
# # # # # #         for j in result.changed
# # # # # #         if j not in direct
# # # # # #     ]

# # # # # #     print("\nDownstream causal changes")
# # # # # #     _line()

# # # # # #     if downstream:

# # # # # #         print(
# # # # # #             f"  {'Feature':<18}"
# # # # # #             f"{'Current':>12}"
# # # # # #             f"{'Result':>12}"
# # # # # #             f"{'Change':>12}"
# # # # # #         )

# # # # # #         print(
# # # # # #             "  "
# # # # # #             + "─" * 54
# # # # # #         )

# # # # # #         for j in downstream:

# # # # # #             old = float(result.x_obs[j])
# # # # # #             new = float(result.x_star[j])
# # # # # #             delta = new - old

# # # # # #             print(
# # # # # #                 f"  {names[j]:<18}"
# # # # # #                 f"{old:>12.3f}"
# # # # # #                 f"{new:>12.3f}"
# # # # # #                 f"{delta:>+12.3f}"
# # # # # #             )

# # # # # #     else:

# # # # # #         print("  None")

# # # # # #     # ============================================================
# # # # # #     # Causal validity
# # # # # #     # ============================================================
# # # # # #     print("\nCausal validity")
# # # # # #     _line()

# # # # # #     if result.violation < 1.5:

# # # # # #         print(
# # # # # #             "  ✓ Resulting state is consistent "
# # # # # #             "with the learned causal structure."
# # # # # #         )

# # # # # #     else:

# # # # # #         print(
# # # # # #             "  ⚠ Resulting state may be inconsistent "
# # # # # #             "with the learned causal structure."
# # # # # #         )

# # # # # #     print(
# # # # # #         f"  Causal distance : "
# # # # # #         f"{result.d_causal:.3f}"
# # # # # #     )

# # # # # #     print(
# # # # # #         f"  Causal sparsity : "
# # # # # #         f"{result.sparsity:.2f}"
# # # # # #     )

# # # # # #     print(
# # # # # #         f"  Runtime         : "
# # # # # #         f"{result.runtime:.3f} sec"
# # # # # #     )

# # # # # # # ================================================================
# # # # # # # 2. CAUSAL FEATURE IMPACT
# # # # # # # ================================================================


# # # # # # def show_attribution(
# # # # # #     result: CAIResult,
# # # # # #     feature_names=None,
# # # # # #     task="regression",
# # # # # # ):
# # # # # #     """
# # # # # #     Display causal feature impact.

# # # # # #     Answers:
# # # # # #         WHICH FEATURES MATTER?
# # # # # #     """

# # # # # #     names = _names(result.x_obs, feature_names)
# # # # # #     cai = np.asarray(result.cai, dtype=float)

# # # # # #     _header("CAUSAL FEATURE IMPACT")

# # # # # #     print(
# # # # # #         "\nThe causal effect estimates how actively changing "
# # # # # #         "each feature influences the model output."
# # # # # #     )
# # # # # #     print()

# # # # # #     _feature_table(cai, names)

# # # # # #     # ------------------------------------------------------------
# # # # # #     # Main driver
# # # # # #     # ------------------------------------------------------------
# # # # # #     order = np.argsort(np.abs(cai))[::-1]
# # # # # #     top = int(order[0])
# # # # # #     top_effect = float(cai[top])

# # # # # #     print("\nMain causal driver")
# # # # # #     _line()
# # # # # #     print(
# # # # # #         f"  {_direction_sentence(names[top], top_effect)}"
# # # # # #     )
# # # # # #     print(
# # # # # #         f"  Estimated effect : {top_effect:+.3f}"
# # # # # #     )

# # # # # #     # ------------------------------------------------------------
# # # # # #     # Reading guide
# # # # # #     # ------------------------------------------------------------
# # # # # #     print("\nHow to read this")
# # # # # #     _line()
# # # # # #     print(
# # # # # #         "  Positive → the intervention moves the outcome upward."
# # # # # #     )
# # # # # #     print(
# # # # # #         "  Negative → the intervention moves the outcome downward."
# # # # # #     )
# # # # # #     print(
# # # # # #         "  Larger absolute value → stronger estimated effect."
# # # # # #     )


# # # # # # # ================================================================
# # # # # # # 3. UNIFIED EXPLANATION
# # # # # # # ================================================================


# # # # # # def show_explanation(
# # # # # #     explanation: UnifiedExplanation,
# # # # # #     feature_names=None,
# # # # # #     task="regression",
# # # # # # ):
# # # # # #     """
# # # # # #     Main CAUSE-XAI user-facing explanation.

# # # # # #     IMPORTANT:
# # # # # #         This intentionally does NOT call:
# # # # # #             show_counterfactual()
# # # # # #             show_attribution()

# # # # # #         because doing so would duplicate information.

# # # # # #     Instead, it creates one compact explanation containing:

# # # # # #         1. Prediction
# # # # # #         2. Main reasons
# # # # # #         3. Counterfactual action
# # # # # #         4. Causal validity
# # # # # #         5. Plain-language conclusion
# # # # # #     """

# # # # # #     names = _names(
# # # # # #         explanation.x_obs,
# # # # # #         feature_names
# # # # # #     )

# # # # # #     cce = explanation.cce
# # # # # #     cai = explanation.cai

# # # # # #     cai_values = np.asarray(
# # # # # #         cai.cai,
# # # # # #         dtype=float
# # # # # #     )

# # # # # #     order = np.argsort(
# # # # # #         np.abs(cai_values)
# # # # # #     )[::-1]

# # # # # #     _header("CAUSE-XAI — MODEL EXPLANATION")

# # # # # #     # ============================================================
# # # # # #     # 1. PREDICTION
# # # # # #     # ============================================================
# # # # # #     print("\n1. PREDICTION")
# # # # # #     _line()

# # # # # #     print(
# # # # # #         f"  Current prediction : "
# # # # # #         f"{explanation.y_fact:.3f}"
# # # # # #     )

# # # # # #     if task == "regression":
# # # # # #         print(
# # # # # #             f"  Requested target  : "
# # # # # #             f"{explanation.y_foil:.3f}"
# # # # # #         )
# # # # # #         print(
# # # # # #             f"  Result             : "
# # # # # #             f"{cce.y_achieved:.3f}"
# # # # # #         )
# # # # # #     else:
# # # # # #         factual_class = int(
# # # # # #             explanation.y_fact >= TARGET_PROB
# # # # # #         )
# # # # # #         achieved_class = int(
# # # # # #             cce.y_achieved >= TARGET_PROB
# # # # # #         )
# # # # # #         print(
# # # # # #             f"  Current class     : "
# # # # # #             f"{factual_class}"
# # # # # #         )
# # # # # #         print(
# # # # # #             f"  Desired class     : "
# # # # # #             f"{int(explanation.y_foil)}"
# # # # # #         )
# # # # # #         print(
# # # # # #             f"  Achieved class    : "
# # # # # #             f"{achieved_class}"
# # # # # #         )

# # # # # #     # ============================================================
# # # # # #     # 2. MAIN FACTORS
# # # # # #     # ============================================================
# # # # # #     print("\n2. MAIN FACTORS")
# # # # # #     _line()

# # # # # #     top_k = min(3, len(order))

# # # # # #     max_name_width = max(
# # # # # #         (len(names[int(order[i])]) for i in range(top_k)),
# # # # # #         default=7
# # # # # #     )
# # # # # #     max_name_width = max(max_name_width, len("Feature"))

# # # # # #     for rank in range(top_k):
# # # # # #         j = int(order[rank])
# # # # # #         effect = float(cai_values[j])
# # # # # #         description = _effect_description(effect)

# # # # # #         print(
# # # # # #             f"  {rank + 1}. "
# # # # # #             f"{names[j]:<{max_name_width}}  "
# # # # # #             f"{effect:>+9.3f}   "
# # # # # #             f"{description}"
# # # # # #         )

# # # # # #     # ============================================================
# # # # # #     # 3. WHAT WOULD CHANGE THE RESULT?
# # # # # #     # ============================================================
# # # # # #     print("\n3. COUNTERFACTUAL — WHAT WOULD NEED TO CHANGE?")
# # # # # #     _line()

# # # # # #     direct = cce.direct_interventions or []

# # # # # #     if cce.feasible:
# # # # # #         if direct:
# # # # # #             for j in direct:
# # # # # #                 old = float(cce.x_obs[j])
# # # # # #                 new = float(cce.x_star[j])

# # # # # #                 print(f"\n  {names[j]}")
# # # # # #                 print(f"    Current : {old:.3f}")
# # # # # #                 print(f"    Desired : {new:.3f}")
# # # # # #                 print(
# # # # # #                     f"    Action  : "
# # # # # #                     f"{_format_change(old, new)}"
# # # # # #                 )

# # # # # #         elif cce.changed:
# # # # # #             for j in cce.changed:
# # # # # #                 old = float(cce.x_obs[j])
# # # # # #                 new = float(cce.x_star[j])

# # # # # #                 print(f"\n  {names[j]}")
# # # # # #                 print(f"    Current : {old:.3f}")
# # # # # #                 print(f"    Desired : {new:.3f}")
# # # # # #                 print(
# # # # # #                     f"    Action  : "
# # # # # #                     f"{_format_change(old, new)}"
# # # # # #                 )

# # # # # #         else:
# # # # # #             print(
# # # # # #                 "  No observable feature change was required."
# # # # # #             )
# # # # # #     else:
# # # # # #         print(
# # # # # #             "  No feasible change was found that reaches "
# # # # # #             f"the requested target of {cce.y_foil:.3f}."
# # # # # #         )
# # # # # #         print(
# # # # # #             "  The target is not reachable under the "
# # # # # #             "current causal constraints."
# # # # # #         )

# # # # # #     # ============================================================
# # # # # #     # 4. CAUSAL VALIDITY
# # # # # #     # ============================================================
# # # # # #     print("\n4. CAUSAL VALIDITY")
# # # # # #     _line()

# # # # # #     if cce.violation < 1.5:
# # # # # #         print(
# # # # # #             "  ✓ The counterfactual remains consistent "
# # # # # #             "with the learned causal structure."
# # # # # #         )
# # # # # #     else:
# # # # # #         print(
# # # # # #             "  ⚠ The counterfactual may violate "
# # # # # #             "the learned causal structure."
# # # # # #         )

# # # # # #     # ============================================================
# # # # # #     # 5. PLAIN LANGUAGE SUMMARY
# # # # # #     # ============================================================
# # # # # #     print("\n5. PLAIN-LANGUAGE SUMMARY")
# # # # # #     _line()

# # # # # #     top = int(order[0])
# # # # # #     top_effect = float(cai_values[top])

# # # # # #     print(
# # # # # #         f"  {_direction_sentence(names[top], top_effect)}"
# # # # # #     )

# # # # # #     if cce.feasible:
# # # # # #         print(
# # # # # #             f"  A feasible causal change can move the "
# # # # # #             f"prediction from {cce.y_fact:.3f} "
# # # # # #             f"to {cce.y_achieved:.3f}."
# # # # # #         )
# # # # # #     else:
# # # # # #         print(
# # # # # #             f"  The requested target of {cce.y_foil:.3f} "
# # # # # #             f"could not be reached with the allowed "
# # # # # #             f"causal interventions."
# # # # # #         )

# # # # # #     print()


# # # # # # # ================================================================
# # # # # # # 4. CAI VS SHAP
# # # # # # # ================================================================


# # # # # # def show_cai_vs_shap(
# # # # # #     comparison: dict,
# # # # # #     feature_names=None,
# # # # # # ):
# # # # # #     """
# # # # # #     Technical comparison between CAI and SHAP-style attribution.
# # # # # #     """

# # # # # #     cai = np.asarray(
# # # # # #         comparison["cai"],
# # # # # #         dtype=float
# # # # # #     )
# # # # # #     shap = np.asarray(
# # # # # #         comparison["shap_style"],
# # # # # #         dtype=float
# # # # # #     )
# # # # # #     names = _names(
# # # # # #         cai,
# # # # # #         feature_names
# # # # # #     )

# # # # # #     difference = cai - shap
# # # # # #     order = np.argsort(
# # # # # #         np.abs(difference)
# # # # # #     )[::-1]

# # # # # #     _header(
# # # # # #         "CAUSAL vs OBSERVATIONAL ATTRIBUTION"
# # # # # #     )

# # # # # #     print(
# # # # # #         "\nCAI:"
# # # # # #     )
# # # # # #     print(
# # # # # #         "  Estimates the effect of actively intervening "
# # # # # #         "on a feature."
# # # # # #     )
# # # # # #     print(
# # # # # #         "\nSHAP-style:"
# # # # # #     )
# # # # # #     print(
# # # # # #         "  Describes the feature's contribution based "
# # # # # #         "on observed relationships."
# # # # # #     )
# # # # # #     print()

# # # # # #     feat_width = 20
# # # # # #     cai_width = 12
# # # # # #     shap_width = 12
# # # # # #     diff_width = 15

# # # # # #     header = (
# # # # # #         f"{'Feature':<{feat_width}}"
# # # # # #         f"{'CAI':>{cai_width}}"
# # # # # #         f"{'SHAP':>{shap_width}}"
# # # # # #         f"{'Difference':>{diff_width}}"
# # # # # #     )
# # # # # #     print(header)
# # # # # #     _line(width=feat_width + cai_width + shap_width + diff_width)

# # # # # #     for j in order:
# # # # # #         row = (
# # # # # #             f"{names[j]:<{feat_width}}"
# # # # # #             f"{cai[j]:>{cai_width}.3f}"
# # # # # #             f"{shap[j]:>{shap_width}.3f}"
# # # # # #             f"{difference[j]:>{diff_width}.3f}"
# # # # # #         )
# # # # # #         print(row)

# # # # # #     print("\nLargest disagreement")
# # # # # #     _line()
# # # # # #     largest = int(order[0])

# # # # # #     print(
# # # # # #         f"  Feature : {names[largest]}"
# # # # # #     )
# # # # # #     print(
# # # # # #         f"  CAI     : {cai[largest]:+.3f}"
# # # # # #     )
# # # # # #     print(
# # # # # #         f"  SHAP    : {shap[largest]:+.3f}"
# # # # # #     )


# # # # # # # ================================================================
# # # # # # # 5. FIT DISPLAY
# # # # # # # ================================================================



# # # # # # def show_fit(
# # # # # #     model,
# # # # # #     feature_names=None,
# # # # # #     verbose=False,
# # # # # # ):
# # # # # #     """
# # # # # #     Compact user-facing fit result.

# # # # # #     Shows:
# # # # # #         - model status
# # # # # #         - causal structure summary
# # # # # #         - causal graph
# # # # # #         - ANM mechanism table

# # # # # #     Detailed ANM fitting rows are shown only when verbose=True.
# # # # # #     """

# # # # # #     _header("CAUSE-XAI — MODEL READY")

# # # # # #     print("\nModel status")
# # # # # #     _line()

# # # # # #     print("  ✓ Causal structure discovered")
# # # # # #     print("  ✓ Causal mechanisms fitted")
# # # # # #     print("  ✓ Model ready for explanation")

# # # # # #     # =========================================================
# # # # # #     # Causal structure
# # # # # #     # =========================================================

# # # # # #     adj = getattr(
# # # # # #         model,
# # # # # #         "_adj",
# # # # # #         None,
# # # # # #     )

# # # # # #     if adj is None:
# # # # # #         adj = getattr(
# # # # # #             model,
# # # # # #             "adj_",
# # # # # #             None,
# # # # # #         )

# # # # # #     if adj is not None:

# # # # # #         adj = np.asarray(adj)

# # # # # #         p = adj.shape[0]

# # # # # #         # -----------------------------------------------------
# # # # # #         # Feature names
# # # # # #         # -----------------------------------------------------

# # # # # #         names = (
# # # # # #             list(feature_names)
# # # # # #             if feature_names is not None
# # # # # #             else getattr(
# # # # # #                 model,
# # # # # #                 "feature_names",
# # # # # #                 None,
# # # # # #             )
# # # # # #         )

# # # # # #         if names is None:
# # # # # #             names = [
# # # # # #                 f"X{i + 1}"
# # # # # #                 for i in range(p)
# # # # # #             ]

# # # # # #         # -----------------------------------------------------
# # # # # #         # Edges
# # # # # #         # -----------------------------------------------------

# # # # # #         edges = []

# # # # # #         for i in range(p):
# # # # # #             for j in range(p):
# # # # # #                 if adj[i, j] != 0:
# # # # # #                     edges.append(
# # # # # #                         (
# # # # # #                             i,
# # # # # #                             j,
# # # # # #                             names[i],
# # # # # #                             names[j],
# # # # # #                         )
# # # # # #                     )

# # # # # #         # -----------------------------------------------------
# # # # # #         # Root / sink nodes
# # # # # #         # -----------------------------------------------------

# # # # # #         parents = {
# # # # # #             j: []
# # # # # #             for j in range(p)
# # # # # #         }

# # # # # #         children = {
# # # # # #             i: []
# # # # # #             for i in range(p)
# # # # # #         }

# # # # # #         for i, j, _, _ in edges:
# # # # # #             parents[j].append(i)
# # # # # #             children[i].append(j)

# # # # # #         root_nodes = [
# # # # # #             names[i]
# # # # # #             for i in range(p)
# # # # # #             if len(parents[i]) == 0
# # # # # #         ]

# # # # # #         sink_nodes = [
# # # # # #             names[i]
# # # # # #             for i in range(p)
# # # # # #             if len(children[i]) == 0
# # # # # #         ]

# # # # # #         # -----------------------------------------------------
# # # # # #         # Causal structure summary
# # # # # #         # -----------------------------------------------------

# # # # # #         print("\nCausal structure")
# # # # # #         _line()

# # # # # #         print(
# # # # # #             f"  Variables                 : {p}"
# # # # # #         )

# # # # # #         print(
# # # # # #             f"  Relationships discovered  : "
# # # # # #             f"{len(edges)}"
# # # # # #         )

# # # # # #         print(
# # # # # #             f"  Root variables            : "
# # # # # #             f"{len(root_nodes)}"
# # # # # #         )

# # # # # #         print(
# # # # # #             f"  Sink variables            : "
# # # # # #             f"{len(sink_nodes)}"
# # # # # #         )

# # # # # #         print(
# # # # # #             "  DAG valid                 : Yes"
# # # # # #         )

# # # # # #         print(
# # # # # #             f"  Root nodes                : "
# # # # # #             f"{', '.join(root_nodes)}"
# # # # # #         )

# # # # # #         print(
# # # # # #             f"  Sink nodes                : "
# # # # # #             f"{', '.join(sink_nodes)}"
# # # # # #         )

# # # # # #         # -----------------------------------------------------
# # # # # #         # Graph
# # # # # #         # -----------------------------------------------------

# # # # # #         try:

# # # # # #             dag = show_dag(
# # # # # #                 model,
# # # # # #                 feature_names=names,
# # # # # #             )

# # # # # #             if dag is not None:

# # # # # #                 output_path = dag.render(
# # # # # #                     "cause_xai_dag",
# # # # # #                     format="png",
# # # # # #                     cleanup=True,
# # # # # #                 )

# # # # # #                 print(
# # # # # #                     "\nCausal graph"
# # # # # #                 )
# # # # # #                 _line()

# # # # # #                 print(
# # # # # #                     f"  DAG saved to: "
# # # # # #                     f"{output_path}"
# # # # # #                 )

# # # # # #         except Exception as e:

# # # # # #             print(
# # # # # #                 "\nCausal graph"
# # # # # #             )
# # # # # #             _line()

# # # # # #             print(
# # # # # #                 f"  Graph unavailable: {e}"
# # # # # #             )

# # # # # #     # =========================================================
# # # # # #     # ANM FIT
# # # # # #     # =========================================================

# # # # # #     if verbose:

# # # # # #         anm = getattr(
# # # # # #             model,
# # # # # #             "anm_",
# # # # # #             None,
# # # # # #         )

# # # # # #         if anm is not None:

# # # # # #             print(
# # # # # #                 "\nCausal mechanism fit"
# # # # # #             )
# # # # # #             _line()

# # # # # #             print(
# # # # # #                 f"  {'Variable':<15}"
# # # # # #                 f"{'Parents':<25}"
# # # # # #                 f"{'Noise':<40}"
# # # # # #                 f"{'Residual std':>15}"
# # # # # #             )

# # # # # #             print(
# # # # # #                 "  "
# # # # # #                 + "─" * 95
# # # # # #             )

# # # # # #             residual_std = getattr(
# # # # # #                 anm,
# # # # # #                 "residual_std",
# # # # # #                 {},
# # # # # #             )

# # # # # #             noise = getattr(
# # # # # #                 anm,
# # # # # #                 "noise",
# # # # # #                 {},
# # # # # #             )

# # # # # #             eqs = getattr(
# # # # # #                 anm,
# # # # # #                 "eqs",
# # # # # #                 {},
# # # # # #             )

# # # # # #             for j in anm.order:

# # # # # #                 # ---------------------------------------------
# # # # # #                 # Variable name
# # # # # #                 # ---------------------------------------------

# # # # # #                 if (
# # # # # #                     feature_names is not None
# # # # # #                     and j < len(feature_names)
# # # # # #                 ):
# # # # # #                     variable = feature_names[j]

# # # # # #                 elif (
# # # # # #                     getattr(
# # # # # #                         anm,
# # # # # #                         "feature_names",
# # # # # #                         None,
# # # # # #                     ) is not None
# # # # # #                     and j < len(
# # # # # #                         anm.feature_names
# # # # # #                     )
# # # # # #                 ):
# # # # # #                     variable = (
# # # # # #                         anm.feature_names[j]
# # # # # #                     )

# # # # # #                 else:
# # # # # #                     variable = f"X{j + 1}"

# # # # # #                 # ---------------------------------------------
# # # # # #                 # Parents
# # # # # #                 # ---------------------------------------------

# # # # # #                 eq = eqs.get(j)

# # # # # #                 if eq is None:
# # # # # #                     parent_names = []

# # # # # #                 else:

# # # # # #                     parent_names = []

# # # # # #                     for p_idx in eq.parents:

# # # # # #                         if (
# # # # # #                             feature_names is not None
# # # # # #                             and p_idx < len(feature_names)
# # # # # #                         ):
# # # # # #                             parent_names.append(
# # # # # #                                 feature_names[p_idx]
# # # # # #                             )

# # # # # #                         elif (
# # # # # #                             getattr(
# # # # # #                                 anm,
# # # # # #                                 "feature_names",
# # # # # #                                 None,
# # # # # #                             ) is not None
# # # # # #                             and p_idx < len(
# # # # # #                                 anm.feature_names
# # # # # #                             )
# # # # # #                         ):
# # # # # #                             parent_names.append(
# # # # # #                                 anm.feature_names[
# # # # # #                                     p_idx
# # # # # #                                 ]
# # # # # #                             )

# # # # # #                         else:
# # # # # #                             parent_names.append(
# # # # # #                                 f"X{p_idx + 1}"
# # # # # #                             )

# # # # # #                 parents_text = (
# # # # # #                     "["
# # # # # #                     + ", ".join(parent_names)
# # # # # #                     + "]"
# # # # # #                 )

# # # # # #                 # ---------------------------------------------
# # # # # #                 # Noise
# # # # # #                 # ---------------------------------------------

# # # # # #                 loc, scale = noise[j]

# # # # # #                 noise_text = (
# # # # # #                     f"Laplace("
# # # # # #                     f"loc={loc:.3f}, "
# # # # # #                     f"scale={scale:.3f})"
# # # # # #                 )

# # # # # #                 # ---------------------------------------------
# # # # # #                 # Residual standard deviation
# # # # # #                 # ---------------------------------------------

# # # # # #                 std = residual_std.get(
# # # # # #                     j,
# # # # # #                     np.nan,
# # # # # #                 )

# # # # # #                 print(
# # # # # #                     f"  {variable:<15}"
# # # # # #                     f"{parents_text:<25}"
# # # # # #                     f"{noise_text:<40}"
# # # # # #                     f"{std:>15.3f}"
# # # # # #                 )

# # # # # #     print()


# # # # # # def show_dag(model, feature_names=None):
# # # # # #     """
# # # # # #     Create a simple Graphviz representation of the learned DAG.

# # # # # #     Returns
# # # # # #     -------
# # # # # #     graphviz.Digraph
# # # # # #         Graphviz graph object.
# # # # # #     """

# # # # # #     import numpy as np

# # # # # #     adj = np.asarray(model._adj)

# # # # # #     p = adj.shape[0]

# # # # # #     if feature_names is not None:
# # # # # #         names = list(feature_names)
# # # # # #     else:
# # # # # #         names = [
# # # # # #             f"X{i + 1}"
# # # # # #             for i in range(p)
# # # # # #         ]

# # # # # #     try:
# # # # # #         from graphviz import Digraph

# # # # # #     except ImportError:
# # # # # #         print(
# # # # # #             "DAG visualization requires Graphviz."
# # # # # #         )
# # # # # #         print(
# # # # # #             "Install Python package with:"
# # # # # #         )
# # # # # #         print(
# # # # # #             "  pip install graphviz"
# # # # # #         )
# # # # # #         return None

# # # # # #     dot = Digraph(
# # # # # #         "CAUSE_XAI_DAG"
# # # # # #     )

# # # # # #     # ------------------------------------------------------------
# # # # # #     # Layout
# # # # # #     # ------------------------------------------------------------

# # # # # #     dot.attr(
# # # # # #         rankdir="LR",
# # # # # #         splines="ortho",
# # # # # #         nodesep="0.45",
# # # # # #         ranksep="0.8",
# # # # # #         bgcolor="white",
# # # # # #     )

# # # # # #     dot.attr(
# # # # # #         "node",
# # # # # #         shape="box",
# # # # # #         style="rounded",
# # # # # #         fontsize="11",
# # # # # #         margin="0.12",
# # # # # #     )

# # # # # #     dot.attr(
# # # # # #         "edge",
# # # # # #         arrowsize="0.7",
# # # # # #         penwidth="1.2",
# # # # # #     )

# # # # # #     # ------------------------------------------------------------
# # # # # #     # Nodes
# # # # # #     # ------------------------------------------------------------

# # # # # #     for i, name in enumerate(names):

# # # # # #         has_parent = np.any(adj[:, i])
# # # # # #         has_child = np.any(adj[i, :])

# # # # # #         if not has_parent:
# # # # # #             label = f"{name}\n(root)"
# # # # # #         elif not has_child:
# # # # # #             label = f"{name}\n(sink)"
# # # # # #         else:
# # # # # #             label = name

# # # # # #         dot.node(
# # # # # #             str(i),
# # # # # #             label
# # # # # #         )

# # # # # #     # ------------------------------------------------------------
# # # # # #     # Edges
# # # # # #     # ------------------------------------------------------------

# # # # # #     for i in range(p):
# # # # # #         for j in range(p):

# # # # # #             if adj[i, j] != 0:

# # # # # #                 dot.edge(
# # # # # #                     str(i),
# # # # # #                     str(j)
# # # # # #                 )

# # # # # #     return dot


# # # # # # def display(
# # # # # #     result,
# # # # # #     feature_names=None,
# # # # # #     task="regression",
# # # # # # ):
# # # # # #     """
# # # # # #     Automatically select the appropriate concise, user-facing display.
# # # # # #     """

# # # # # #     if isinstance(
# # # # # #         result,
# # # # # #         UnifiedExplanation
# # # # # #     ):
# # # # # #         show_explanation(
# # # # # #             result,
# # # # # #             feature_names=feature_names,
# # # # # #             task=task,
# # # # # #         )

# # # # # #     elif isinstance(
# # # # # #         result,
# # # # # #         CCEResult
# # # # # #     ):
# # # # # #         show_counterfactual(
# # # # # #             result,
# # # # # #             feature_names=feature_names,
# # # # # #             task=task,
# # # # # #         )

# # # # # #     elif isinstance(
# # # # # #         result,
# # # # # #         CAIResult
# # # # # #     ):
# # # # # #         show_attribution(
# # # # # #             result,
# # # # # #             feature_names=feature_names,
# # # # # #             task=task,
# # # # # #         )

# # # # # #     elif isinstance(result, dict):
# # # # # #         if (
# # # # # #             "cai" in result
# # # # # #             and "shap_style" in result
# # # # # #         ):
# # # # # #             show_cai_vs_shap(
# # # # # #                 result,
# # # # # #                 feature_names=feature_names,
# # # # # #             )
# # # # # #         else:
# # # # # #             raise TypeError(
# # # # # #                 "Dictionary does not contain a recognised "
# # # # # #                 "CAUSE-XAI result."
# # # # # #             )

# # # # # #     else:
# # # # # #         raise TypeError(
# # # # # #             f"Unsupported result type: "
# # # # # #             f"{type(result).__name__}"
# # # # # #         )


# # # # # # __all__ = [
# # # # # #     "show_fit",
# # # # # #     "show_counterfactual",
# # # # # #     "show_attribution",
# # # # # #     "show_explanation",
# # # # # #     "show_cai_vs_shap",
# # # # # #     "display",
# # # # # # ]

# # # # # """
# # # # # User-facing display layer for CAUSE-XAI.

# # # # # The result classes contain numerical results.
# # # # # This module converts those results into concise,
# # # # # human-readable explanations.

# # # # # Main principle
# # # # # --------------
# # # # # Results store numbers.
# # # # # Display explains those numbers.

# # # # # The primary user-facing explanation should answer:

# # # # #     - What was predicted?
# # # # #     - Which features causally influenced it?
# # # # #     - What happens under intervention?
# # # # #     - What would need to change?
# # # # #     - Is the counterfactual causally feasible?

# # # # # CAI
# # # # # ---
# # # # # CAI_j = E[f | do(X_j = x_j)] - E[f]

# # # # # SHAP-style comparison
# # # # # ---------------------
# # # # # SHAP-style_j ≈ E[f | X_j = x_j] - E[f]

# # # # # The distinction is important:

# # # # #     CAI      -> intervention
# # # # #     SHAP     -> observational association
# # # # # """

# # # # # import numpy as np
# # # # # import matplotlib.pyplot as plt

# # # # # from .config import TARGET_PROB
# # # # # from .results import (
# # # # #     CCEResult,
# # # # #     CAIResult,
# # # # #     UnifiedExplanation,
# # # # # )


# # # # # # ================================================================
# # # # # # BASIC HELPERS
# # # # # # ================================================================


# # # # # def _names(values, feature_names=None):
# # # # #     """
# # # # #     Return readable feature names.
# # # # #     """

# # # # #     n = len(values)

# # # # #     if feature_names is not None:

# # # # #         if len(feature_names) != n:
# # # # #             raise ValueError(
# # # # #                 "feature_names must have the same length "
# # # # #                 "as the features."
# # # # #             )

# # # # #         return list(feature_names)

# # # # #     return [
# # # # #         f"Feature {i + 1}"
# # # # #         for i in range(n)
# # # # #     ]


# # # # # def _line(char="─", width=78):
# # # # #     print(char * width)


# # # # # def _header(title, width=78):
# # # # #     print()
# # # # #     print("═" * width)
# # # # #     print(title.center(width))
# # # # #     print("═" * width)


# # # # # def _format_change(old, new):
# # # # #     """
# # # # #     Convert numerical change into readable language.
# # # # #     """

# # # # #     old = float(old)
# # # # #     new = float(new)

# # # # #     delta = new - old

# # # # #     if abs(delta) < 1e-10:
# # # # #         return "no change"

# # # # #     if delta > 0:
# # # # #         return f"increase by {abs(delta):.3f}"

# # # # #     return f"decrease by {abs(delta):.3f}"


# # # # # def _effect_description(effect, reference=None):
# # # # #     """
# # # # #     Convert a CAI value into a human-readable description.

# # # # #     CAI values are model-output effects. Therefore fixed
# # # # #     thresholds such as 10 or 20 are inappropriate for
# # # # #     probability/regression outputs.

# # # # #     If reference is supplied, magnitude is interpreted
# # # # #     relative to the largest absolute causal effect.
# # # # #     """

# # # # #     effect = float(effect)

# # # # #     if abs(effect) < 1e-10:
# # # # #         return "Little measurable causal influence"

# # # # #     magnitude = abs(effect)

# # # # #     if reference is None:
# # # # #         reference = magnitude

# # # # #     reference = max(float(reference), 1e-10)

# # # # #     relative = magnitude / reference

# # # # #     if effect > 0:

# # # # #         if relative >= 0.75:
# # # # #             return "Strong upward causal influence"

# # # # #         if relative >= 0.35:
# # # # #             return "Moderate upward causal influence"

# # # # #         return "Smaller upward causal influence"

# # # # #     else:

# # # # #         if relative >= 0.75:
# # # # #             return "Strong downward causal influence"

# # # # #         if relative >= 0.35:
# # # # #             return "Moderate downward causal influence"

# # # # #         return "Smaller downward causal influence"


# # # # # def _direction_sentence(feature, effect):
# # # # #     """
# # # # #     Create a natural-language explanation for a causal effect.
# # # # #     """

# # # # #     effect = float(effect)

# # # # #     if effect > 0:
# # # # #         return (
# # # # #             f"{feature} is the strongest causal factor "
# # # # #             f"increasing the predicted outcome."
# # # # #         )

# # # # #     if effect < 0:
# # # # #         return (
# # # # #             f"{feature} is the strongest causal factor "
# # # # #             f"decreasing the predicted outcome."
# # # # #         )

# # # # #     return (
# # # # #         f"{feature} has little measurable causal influence "
# # # # #         f"on the predicted outcome."
# # # # #     )


# # # # # def _format_ci(ci):
# # # # #     """
# # # # #     Format a confidence interval safely.
# # # # #     """

# # # # #     if ci is None:
# # # # #         return "N/A"

# # # # #     try:
# # # # #         return (
# # # # #             f"[{float(ci[0]):+.4f}, "
# # # # #             f"{float(ci[1]):+.4f}]"
# # # # #         )
# # # # #     except Exception:
# # # # #         return "N/A"


# # # # # # ================================================================
# # # # # # CAUSAL IMPACT TABLE
# # # # # # ================================================================


# # # # # def _feature_table(result, names):
# # # # #     """
# # # # #     Display CAI values.

# # # # #     If Monte Carlo diagnostics are available, display:

# # # # #         Feature
# # # # #         CAI
# # # # #         SE
# # # # #         95% CI
# # # # #         Interpretation

# # # # #     Otherwise display the simpler CAI table.
# # # # #     """

# # # # #     cai = np.asarray(
# # # # #         result.cai,
# # # # #         dtype=float,
# # # # #     )

# # # # #     order = np.argsort(
# # # # #         np.abs(cai)
# # # # #     )[::-1]

# # # # #     max_effect = (
# # # # #         np.max(np.abs(cai))
# # # # #         if len(cai)
# # # # #         else 0.0
# # # # #     )

# # # # #     has_uncertainty = (
# # # # #         result.standard_errors is not None
# # # # #         and result.confidence_intervals is not None
# # # # #     )

# # # # #     if has_uncertainty:

# # # # #         print(
# # # # #             f"{'Feature':<20}"
# # # # #             f"{'CAI':>12}"
# # # # #             f"{'SE':>12}"
# # # # #             f"{'95% CI':>25}"
# # # # #         )

# # # # #         _line(width=69)

# # # # #         for j in order:

# # # # #             ci = result.confidence_intervals[j]

# # # # #             print(
# # # # #                 f"{names[j]:<20}"
# # # # #                 f"{cai[j]:>+12.4f}"
# # # # #                 f"{result.standard_errors[j]:>12.4f}"
# # # # #                 f"{_format_ci(ci):>25}"
# # # # #             )

# # # # #     else:

# # # # #         print(
# # # # #             f"{'Feature':<20}"
# # # # #             f"{'CAI':>12}"
# # # # #             f"{'Interpretation':>40}"
# # # # #         )

# # # # #         _line(width=72)

# # # # #         for j in order:

# # # # #             effect = float(cai[j])

# # # # #             print(
# # # # #                 f"{names[j]:<20}"
# # # # #                 f"{effect:>+12.4f}"
# # # # #                 f"{_effect_description(effect, max_effect):>40}"
# # # # #             )


# # # # # # ================================================================
# # # # # # 1. COUNTERFACTUAL
# # # # # # ================================================================


# # # # # def show_counterfactual(
# # # # #     result: CCEResult,
# # # # #     feature_names=None,
# # # # #     task="regression",
# # # # # ):
# # # # #     """
# # # # #     Display the causal counterfactual result.

# # # # #     Separates:

# # # # #         1. Direct changes
# # # # #         2. Downstream causal changes
# # # # #         3. Causal validity
# # # # #     """

# # # # #     names = _names(
# # # # #         result.x_obs,
# # # # #         feature_names,
# # # # #     )

# # # # #     _header(
# # # # #         "COUNTERFACTUAL EXPLANATION"
# # # # #     )

# # # # #     # ============================================================
# # # # #     # Prediction
# # # # #     # ============================================================

# # # # #     print("\nPrediction")
# # # # #     _line()

# # # # #     print(
# # # # #         f"  Current prediction : "
# # # # #         f"{result.y_fact:.3f}"
# # # # #     )

# # # # #     print(
# # # # #         f"  Target prediction  : "
# # # # #         f"{result.y_foil:.3f}"
# # # # #     )

# # # # #     print(
# # # # #         f"  Achieved prediction: "
# # # # #         f"{result.y_achieved:.3f}"
# # # # #     )

# # # # #     print(
# # # # #         f"  Target reached     : "
# # # # #         f"{'YES' if result.feasible else 'NO'}"
# # # # #     )

# # # # #     # ============================================================
# # # # #     # Direct changes
# # # # #     # ============================================================

# # # # #     direct = result.direct_interventions or []

# # # # #     print("\nDirect changes")
# # # # #     _line()

# # # # #     if direct:

# # # # #         print(
# # # # #             f"  {'Feature':<18}"
# # # # #             f"{'Current':>12}"
# # # # #             f"{'Desired':>12}"
# # # # #             f"{'Action':>22}"
# # # # #         )

# # # # #         print(
# # # # #             "  "
# # # # #             + "─" * 64
# # # # #         )

# # # # #         for j in direct:

# # # # #             old = float(
# # # # #                 result.x_obs[j]
# # # # #             )

# # # # #             new = float(
# # # # #                 result.x_star[j]
# # # # #             )

# # # # #             print(
# # # # #                 f"  {names[j]:<18}"
# # # # #                 f"{old:>12.3f}"
# # # # #                 f"{new:>12.3f}"
# # # # #                 f"{_format_change(old, new):>22}"
# # # # #             )

# # # # #     else:

# # # # #         print("  None")

# # # # #     # ============================================================
# # # # #     # Downstream causal changes
# # # # #     # ============================================================

# # # # #     changed = getattr(
# # # # #         result,
# # # # #         "changed",
# # # # #         [],
# # # # #     ) or []

# # # # #     downstream = [
# # # # #         j
# # # # #         for j in changed
# # # # #         if j not in direct
# # # # #     ]

# # # # #     print(
# # # # #         "\nDownstream causal changes"
# # # # #     )

# # # # #     _line()

# # # # #     if downstream:

# # # # #         print(
# # # # #             f"  {'Feature':<18}"
# # # # #             f"{'Current':>12}"
# # # # #             f"{'Result':>12}"
# # # # #             f"{'Change':>12}"
# # # # #         )

# # # # #         print(
# # # # #             "  "
# # # # #             + "─" * 54
# # # # #         )

# # # # #         for j in downstream:

# # # # #             old = float(
# # # # #                 result.x_obs[j]
# # # # #             )

# # # # #             new = float(
# # # # #                 result.x_star[j]
# # # # #             )

# # # # #             print(
# # # # #                 f"  {names[j]:<18}"
# # # # #                 f"{old:>12.3f}"
# # # # #                 f"{new:>12.3f}"
# # # # #                 f"{new - old:>+12.3f}"
# # # # #             )

# # # # #     else:

# # # # #         print("  None")

# # # # #     # ============================================================
# # # # #     # Causal validity
# # # # #     # ============================================================

# # # # #     print("\nCausal validity")
# # # # #     _line()

# # # # #     violation = float(
# # # # #         getattr(
# # # # #             result,
# # # # #             "violation",
# # # # #             0.0,
# # # # #         )
# # # # #     )

# # # # #     if violation < 1.5:

# # # # #         print(
# # # # #             "  ✓ Resulting state is consistent "
# # # # #             "with the learned causal structure."
# # # # #         )

# # # # #     else:

# # # # #         print(
# # # # #             "  ⚠ Resulting state may be inconsistent "
# # # # #             "with the learned causal structure."
# # # # #         )

# # # # #     if hasattr(result, "d_causal"):
# # # # #         print(
# # # # #             f"  Causal distance : "
# # # # #             f"{result.d_causal:.3f}"
# # # # #         )

# # # # #     if hasattr(result, "sparsity"):
# # # # #         print(
# # # # #             f"  Causal sparsity : "
# # # # #             f"{result.sparsity:.2f}"
# # # # #         )

# # # # #     if hasattr(result, "runtime"):
# # # # #         print(
# # # # #             f"  Runtime         : "
# # # # #             f"{result.runtime:.3f} sec"
# # # # #         )

# # # # #     print()


# # # # # # ================================================================
# # # # # # 2. CAUSAL FEATURE IMPACT / CAI
# # # # # # ================================================================


# # # # # def show_attribution(
# # # # #     result: CAIResult,
# # # # #     feature_names=None,
# # # # # ):
# # # # #     """
# # # # #     Display CAI results.

# # # # #     The function only displays values already computed in CAIResult.
# # # # #     No task-specific logic is required here.
# # # # #     """

# # # # #     names = _names(
# # # # #         result.x_obs,
# # # # #         feature_names,
# # # # #     )

# # # # #     cai = np.asarray(result.cai, dtype=float)

# # # # #     if cai.size == 0:
# # # # #         _header("CAUSAL FEATURE IMPACT")
# # # # #         print("\n  No CAI values available.")
# # # # #         return

# # # # #     # ---------------------------------------------------------
# # # # #     # Sort by absolute causal impact
# # # # #     # ---------------------------------------------------------

# # # # #     order = np.argsort(np.abs(cai))[::-1]

# # # # #     top = int(order[0])
# # # # #     top_effect = float(cai[top])

# # # # #     _header("CAUSAL FEATURE IMPACT")

# # # # #     # ---------------------------------------------------------
# # # # #     # Monte Carlo information
# # # # #     # ---------------------------------------------------------

# # # # #     if result.n_samples is not None:
# # # # #         print(
# # # # #             f"\nMonte Carlo samples : {result.n_samples}"
# # # # #         )

# # # # #     print(
# # # # #         f"Baseline E[f(X)]    : {result.baseline:.4f}"
# # # # #     )

# # # # #     # ---------------------------------------------------------
# # # # #     # Feature-level table
# # # # #     # ---------------------------------------------------------

# # # # #     print("\nFeature-level causal effects")
# # # # #     _line()

# # # # #     # Header
# # # # #     print(
# # # # #         f"{'Rank':>4}  "
# # # # #         f"{'Feature':<28} "
# # # # #         f"{'Intervention':>13} "
# # # # #         f"{'E[f|do]':>10} "
# # # # #         f"{'CAI':>9} "
# # # # #         f"{'SE':>8} "
# # # # #         f"{'95% CI':>23}"
# # # # #     )

# # # # #     print(
# # # # #         "────  "
# # # # #         "──────────────────────────── "
# # # # #         "───────────── "
# # # # #         "────────── "
# # # # #         "───────── "
# # # # #         "──────── "
# # # # #         "───────────────────────"
# # # # #     )

# # # # #     # ---------------------------------------------------------
# # # # #     # Rows
# # # # #     # ---------------------------------------------------------

# # # # #     for rank, j in enumerate(order, start=1):

# # # # #         name = str(names[j])

# # # # #         # Intervention value
# # # # #         intervention = float(result.x_obs[j])

# # # # #         # Expected output under intervention
# # # # #         f_do = float(result.f_do[j])

# # # # #         # CAI
# # # # #         effect = float(result.cai[j])

# # # # #         # Standard error
# # # # #         if result.standard_errors is not None:
# # # # #             se = float(result.standard_errors[j])
# # # # #             se_text = f"{se:.4f}"
# # # # #         else:
# # # # #             se_text = "—"

# # # # #         # Confidence interval
# # # # #         if result.confidence_intervals is not None:

# # # # #             lo = float(
# # # # #                 result.confidence_intervals[j, 0]
# # # # #             )

# # # # #             hi = float(
# # # # #                 result.confidence_intervals[j, 1]
# # # # #             )

# # # # #             ci_text = (
# # # # #                 f"[{lo:+.4f}, {hi:+.4f}]"
# # # # #             )

# # # # #         else:
# # # # #             ci_text = "—"

# # # # #         print(
# # # # #             f"{rank:>4}  "
# # # # #             f"{name:<28} "
# # # # #             f"{intervention:+13.3f} "
# # # # #             f"{f_do:10.4f} "
# # # # #             f"{effect:+9.4f} "
# # # # #             f"{se_text:>8} "
# # # # #             f"{ci_text:>23}"
# # # # #         )

# # # # #     # ---------------------------------------------------------
# # # # #     # Main causal driver
# # # # #     # ---------------------------------------------------------

# # # # #     print("\nMain causal driver")
# # # # #     _line()

# # # # #     direction = (
# # # # #         "increases"
# # # # #         if top_effect > 0
# # # # #         else "decreases"
# # # # #         if top_effect < 0
# # # # #         else "has approximately no effect on"
# # # # #     )

# # # # #     print(
# # # # #         f"  {names[top]} is the strongest causal factor "
# # # # #         f"and {direction} the model output."
# # # # #     )

# # # # #     print(
# # # # #         f"  CAI : {top_effect:+.4f}"
# # # # #     )

# # # # #     if (
# # # # #         result.standard_errors is not None
# # # # #         and result.confidence_intervals is not None
# # # # #     ):

# # # # #         print(
# # # # #             f"  SE  : "
# # # # #             f"{result.standard_errors[top]:.4f}"
# # # # #         )

# # # # #         lo = result.confidence_intervals[top, 0]
# # # # #         hi = result.confidence_intervals[top, 1]

# # # # #         print(
# # # # #             f"  95% CI : "
# # # # #             f"[{lo:+.4f}, {hi:+.4f}]"
# # # # #         )

# # # # #     print()
# # # # # # ================================================================
# # # # # # 3. UNIFIED EXPLANATION
# # # # # # ================================================================


# # # # # def show_explanation(
# # # # #     explanation: UnifiedExplanation,
# # # # #     feature_names=None,
# # # # # ):
# # # # #     """
# # # # #     Display the unified CAUSE-XAI explanation.

# # # # #     Combines:
# # # # #         1. Prediction / target
# # # # #         2. Main causal factors
# # # # #         3. Counterfactual action
# # # # #         4. Causal validity
# # # # #         5. Plain-language conclusion

# # # # #     The display is task-independent.
# # # # #     No calculations or task-specific assumptions are introduced here.
# # # # #     """

# # # # #     names = _names(
# # # # #         explanation.x_obs,
# # # # #         feature_names,
# # # # #     )

# # # # #     cce = explanation.cce
# # # # #     cai = explanation.cai

# # # # #     cai_values = np.asarray(
# # # # #         cai.cai,
# # # # #         dtype=float,
# # # # #     )

# # # # #     if cai_values.size == 0:
# # # # #         _header(
# # # # #             "CAUSE-XAI — MODEL EXPLANATION"
# # # # #         )
# # # # #         print("\n  No causal attribution values available.")
# # # # #         return

# # # # #     order = np.argsort(
# # # # #         np.abs(cai_values)
# # # # #     )[::-1]

# # # # #     top_k = min(
# # # # #         5,
# # # # #         len(order),
# # # # #     )

# # # # #     top = int(order[0])
# # # # #     top_effect = float(cai_values[top])

# # # # #     _header(
# # # # #         "CAUSE-XAI — MODEL EXPLANATION"
# # # # #     )

# # # # #     # ============================================================
# # # # #     # 1. HIGH-LEVEL EXPLANATION
# # # # #     # ============================================================

# # # # #     print("\n1. EXPLANATION OVERVIEW")
# # # # #     _line()

# # # # #     print(
# # # # #         f"  Prediction          : "
# # # # #         f"{explanation.y_fact:.4f}"
# # # # #     )

# # # # #     print(
# # # # #         f"  Target              : "
# # # # #         f"{explanation.y_foil:.4f}"
# # # # #     )

# # # # #     print(
# # # # #         f"  Achieved prediction : "
# # # # #         f"{cce.y_achieved:.4f}"
# # # # #     )

# # # # #     # ------------------------------------------------------------
# # # # #     # Feasibility
# # # # #     # ------------------------------------------------------------

# # # # #     if cce.feasible:
# # # # #         print(
# # # # #             "  Feasibility         : ✓ Feasible"
# # # # #         )
# # # # #     else:
# # # # #         print(
# # # # #             "  Feasibility         : ✗ No feasible "
# # # # #             "counterfactual found"
# # # # #         )

# # # # #     # ------------------------------------------------------------
# # # # #     # Causal metrics
# # # # #     # ------------------------------------------------------------

# # # # #     direct = (
# # # # #         cce.direct_interventions
# # # # #         or []
# # # # #     )

# # # # #     changed = (
# # # # #         cce.changed
# # # # #         or []
# # # # #     )

# # # # #     downstream = max(
# # # # #         0,
# # # # #         len(changed) - len(direct),
# # # # #     )

# # # # #     print(
# # # # #         f"  Direct interventions: "
# # # # #         f"{len(direct)}"
# # # # #     )

# # # # #     print(
# # # # #         f"  Downstream changes  : "
# # # # #         f"{downstream}"
# # # # #     )

# # # # #     print(
# # # # #         f"  Causal sparsity     : "
# # # # #         f"{getattr(cce, 'sparsity', 0.0):.4f}"
# # # # #     )

# # # # #     violation = float(
# # # # #         getattr(
# # # # #             cce,
# # # # #             "violation",
# # # # #             0.0,
# # # # #         )
# # # # #     )

# # # # #     print(
# # # # #         f"  Causal violation    : "
# # # # #         f"{violation:.4f}"
# # # # #     )

# # # # #     runtime = getattr(
# # # # #         cce,
# # # # #         "runtime",
# # # # #         None,
# # # # #     )

# # # # #     if runtime is not None:
# # # # #         print(
# # # # #             f"  Runtime             : "
# # # # #             f"{float(runtime):.4f} s"
# # # # #         )

# # # # #     # ============================================================
# # # # #     # 2. WHY THIS PREDICTION?
# # # # #     # ============================================================

# # # # #     print("\n2. WHY THIS PREDICTION?")
# # # # #     _line()

# # # # #     print(
# # # # #         f"  {_direction_sentence(names[top], top_effect)}"
# # # # #     )

# # # # #     print(
# # # # #         f"  Top causal driver   : "
# # # # #         f"{names[top]}"
# # # # #     )

# # # # #     print(
# # # # #         f"  CAI                 : "
# # # # #         f"{top_effect:+.4f}"
# # # # #     )

# # # # #     # ============================================================
# # # # #     # 3. WHAT WOULD NEED TO CHANGE?
# # # # #     # ============================================================

# # # # #     print(
# # # # #         "\n3. WHAT WOULD NEED TO CHANGE?"
# # # # #     )

# # # # #     _line()

# # # # #     if cce.feasible:

# # # # #         direct = (
# # # # #             cce.direct_interventions
# # # # #             or []
# # # # #         )

# # # # #         changed = (
# # # # #             cce.changed
# # # # #             or []
# # # # #         )

# # # # #         # Prefer direct interventions.
# # # # #         # Fall back to changed features if necessary.
# # # # #         display_indices = (
# # # # #             direct
# # # # #             if direct
# # # # #             else changed
# # # # #         )

# # # # #         if display_indices:

# # # # #             for j in display_indices:

# # # # #                 old = float(
# # # # #                     cce.x_obs[j]
# # # # #                 )

# # # # #                 new = float(
# # # # #                     cce.x_star[j]
# # # # #                 )

# # # # #                 delta = new - old

# # # # #                 marker = (
# # # # #                     "★ "
# # # # #                     if j in direct
# # # # #                     else "  "
# # # # #                 )

# # # # #                 print(
# # # # #                     f"\n  {marker}{names[j]}"
# # # # #                 )

# # # # #                 print(
# # # # #                     f"      Current : "
# # # # #                     f"{old:+.4f}"
# # # # #                 )

# # # # #                 print(
# # # # #                     f"      Changed : "
# # # # #                     f"{new:+.4f}"
# # # # #                 )

# # # # #                 print(
# # # # #                     f"      Δ       : "
# # # # #                     f"{delta:+.4f}"
# # # # #                 )

# # # # #                 print(
# # # # #                     f"      Action  : "
# # # # #                     f"{_format_change(old, new)}"
# # # # #                 )

# # # # #         else:

# # # # #             print(
# # # # #                 "  No observable feature change "
# # # # #                 "was required."
# # # # #             )

# # # # #     else:

# # # # #         print(
# # # # #             "  No feasible counterfactual was found "
# # # # #             "for the requested target."
# # # # #         )

# # # # #     # ============================================================
# # # # #     # 4. CAUSAL IMPACT — TOP FEATURES
# # # # #     # ============================================================

# # # # #     print(
# # # # #         "\n4. TOP CAUSAL FACTORS"
# # # # #     )

# # # # #     _line()

# # # # #     print(
# # # # #         f"{'Rank':>4}  "
# # # # #         f"{'Feature':<28} "
# # # # #         f"{'CAI':>10}"
# # # # #     )

# # # # #     _line(width=48)

# # # # #     for rank in range(top_k):

# # # # #         j = int(
# # # # #             order[rank]
# # # # #         )

# # # # #         print(
# # # # #             f"{rank + 1:>4}  "
# # # # #             f"{names[j]:<28.28} "
# # # # #             f"{cai_values[j]:>+10.4f}"
# # # # #         )

# # # # #     # ============================================================
# # # # #     # 5. CAUSAL VALIDITY
# # # # #     # ============================================================

# # # # #     print(
# # # # #         "\n5. CAUSAL VALIDITY"
# # # # #     )

# # # # #     _line()

# # # # #     if violation < 1.5:

# # # # #         print(
# # # # #             "  ✓ Counterfactual is consistent "
# # # # #             "with the learned causal structure."
# # # # #         )

# # # # #     else:

# # # # #         print(
# # # # #             "  ⚠ Counterfactual may violate "
# # # # #             "the learned causal structure."
# # # # #         )

# # # # #     # ============================================================
# # # # #     # 6. PLAIN-LANGUAGE CONCLUSION
# # # # #     # ============================================================

# # # # #     print(
# # # # #         "\n6. CONCLUSION"
# # # # #     )

# # # # #     _line()

# # # # #     print(
# # # # #         f"  Why: {names[top]} has the strongest "
# # # # #         f"causal influence "
# # # # #         f"(CAI = {top_effect:+.4f})."
# # # # #     )

# # # # #     if cce.feasible:

# # # # #         if direct:

# # # # #             direct_names = [
# # # # #                 names[j]
# # # # #                 for j in direct
# # # # #             ]

# # # # #             print(
# # # # #                 "  Action: intervene on "
# # # # #                 + ", ".join(direct_names)
# # # # #                 + " to obtain the requested "
# # # # #                   "counterfactual outcome."
# # # # #             )

# # # # #         print(
# # # # #             f"  Result: prediction changes from "
# # # # #             f"{cce.y_fact:.4f} to "
# # # # #             f"{cce.y_achieved:.4f}."
# # # # #         )

# # # # #     else:

# # # # #         print(
# # # # #             "  Result: the requested target could "
# # # # #             "not be reached under the learned "
# # # # #             "causal constraints."
# # # # #         )

# # # # #     print()
# # # # # # ================================================================
# # # # # # 4. CAI VS SHAP
# # # # # # ================================================================


# # # # # def show_cai_vs_shap(
# # # # #     comparison: dict,
# # # # #     feature_names=None,
# # # # # ):
# # # # #     """
# # # # #     Display CAI vs SHAP comparison.

# # # # #     Includes:
# # # # #     - CAI vs SHAP scatter plot
# # # # #     - Difference bar chart
# # # # #     - Feature comparison table
# # # # #     - Reference outputs
# # # # #     - Bias summary
# # # # #     - Largest disagreement

# # # # #     No task argument is required.
# # # # #     """

# # # # #     if not isinstance(comparison, dict):
# # # # #         raise TypeError(
# # # # #             "comparison must be a dictionary."
# # # # #         )

# # # # #     required = {
# # # # #         "cai",
# # # # #         "shap_style",
# # # # #         "baseline_int",
# # # # #         "baseline_obs",
# # # # #     }

# # # # #     missing = [
# # # # #         key for key in required
# # # # #         if key not in comparison
# # # # #     ]

# # # # #     if missing:
# # # # #         raise KeyError(
# # # # #             "CAI vs SHAP comparison is missing: "
# # # # #             + ", ".join(missing)
# # # # #         )

# # # # #     cai = np.asarray(
# # # # #         comparison["cai"],
# # # # #         dtype=float,
# # # # #     )

# # # # #     shap = np.asarray(
# # # # #         comparison["shap_style"],
# # # # #         dtype=float,
# # # # #     )

# # # # #     if cai.shape != shap.shape:
# # # # #         raise ValueError(
# # # # #             "CAI and SHAP arrays must have the same shape."
# # # # #         )

# # # # #     names = _names(
# # # # #         cai,
# # # # #         feature_names,
# # # # #     )

# # # # #     difference = cai - shap

# # # # #     bias_threshold = 0.05

# # # # #     order = np.argsort(
# # # # #         np.abs(difference)
# # # # #     )[::-1]

# # # # #     # ============================================================
# # # # #     # HEADER
# # # # #     # ============================================================

# # # # #     _header(
# # # # #         "CAUSAL vs OBSERVATIONAL ATTRIBUTION"
# # # # #     )

# # # # #     # ============================================================
# # # # #     # REFERENCE OUTPUTS
# # # # #     # ============================================================

# # # # #     print("\nReference outputs")
# # # # #     _line()

# # # # #     print(
# # # # #         f"  Interventional baseline : "
# # # # #         f"{comparison['baseline_int']:.4f}"
# # # # #     )

# # # # #     print(
# # # # #         f"  Observational baseline  : "
# # # # #         f"{comparison['baseline_obs']:.4f}"
# # # # #     )

# # # # #     # ============================================================
# # # # #     # VISUAL 1 : CAI VS SHAP
# # # # #     # ============================================================

# # # # #     import matplotlib.pyplot as plt

# # # # #     fig, ax = plt.subplots(
# # # # #         figsize=(8, 6)
# # # # #     )

# # # # #     ax.scatter(
# # # # #         shap,
# # # # #         cai,
# # # # #         s=55,
# # # # #         alpha=0.8,
# # # # #     )

# # # # #     min_val = min(
# # # # #         np.min(shap),
# # # # #         np.min(cai),
# # # # #     )

# # # # #     max_val = max(
# # # # #         np.max(shap),
# # # # #         np.max(cai),
# # # # #     )

# # # # #     padding = (
# # # # #         max_val - min_val
# # # # #     ) * 0.08

# # # # #     ax.plot(
# # # # #         [min_val - padding, max_val + padding],
# # # # #         [min_val - padding, max_val + padding],
# # # # #         linestyle="--",
# # # # #         linewidth=1,
# # # # #     )

# # # # #     for i, name in enumerate(names):
# # # # #         ax.annotate(
# # # # #             name,
# # # # #             (shap[i], cai[i]),
# # # # #             xytext=(4, 4),
# # # # #             textcoords="offset points",
# # # # #             fontsize=8,
# # # # #         )

# # # # #     ax.set_xlabel(
# # # # #         "SHAP-style attribution"
# # # # #     )

# # # # #     ax.set_ylabel(
# # # # #         "Causal Attribution Index (CAI)"
# # # # #     )

# # # # #     ax.set_title(
# # # # #         "CAI vs SHAP-style Attribution"
# # # # #     )

# # # # #     ax.grid(
# # # # #         alpha=0.25
# # # # #     )

# # # # #     plt.tight_layout()
# # # # #     plt.show()

# # # # #     # ============================================================
# # # # #     # VISUAL 2 : DIFFERENCE BAR CHART
# # # # #     # ============================================================

# # # # #     sorted_names = [
# # # # #         names[i]
# # # # #         for i in order
# # # # #     ]

# # # # #     sorted_difference = difference[
# # # # #         order
# # # # #     ]

# # # # #     fig, ax = plt.subplots(
# # # # #         figsize=(10, 7)
# # # # #     )

# # # # #     ax.barh(
# # # # #         sorted_names[::-1],
# # # # #         sorted_difference[::-1],
# # # # #     )

# # # # #     ax.axvline(
# # # # #         0,
# # # # #         linewidth=1,
# # # # #     )

# # # # #     ax.set_xlabel(
# # # # #         "CAI − SHAP"
# # # # #     )

# # # # #     ax.set_ylabel(
# # # # #         "Feature"
# # # # #     )

# # # # #     ax.set_title(
# # # # #         "Where do CAI and SHAP Disagree?"
# # # # #     )

# # # # #     ax.grid(
# # # # #         axis="x",
# # # # #         alpha=0.25,
# # # # #     )

# # # # #     plt.tight_layout()
# # # # #     plt.show()

# # # # #     # ============================================================
# # # # #     # FEATURE COMPARISON TABLE
# # # # #     # ============================================================

# # # # #     print("\nFeature comparison")
# # # # #     _line(width=78)

# # # # #     print(
# # # # #         f"{'Rank':>4}  "
# # # # #         f"{'Feature':<28} "
# # # # #         f"{'CAI (do)':>11} "
# # # # #         f"{'SHAP (obs)':>12} "
# # # # #         f"{'Difference':>12} "
# # # # #         f"{'Bias?':>7}"
# # # # #     )

# # # # #     _line(width=78)

# # # # #     for rank, j in enumerate(order, start=1):

# # # # #         diff = float(
# # # # #             difference[j]
# # # # #         )

# # # # #         biased = (
# # # # #             abs(diff)
# # # # #             > bias_threshold
# # # # #         )

# # # # #         flag = "YES" if biased else "—"

# # # # #         print(
# # # # #             f"{rank:>4}  "
# # # # #             f"{names[j]:<28.28} "
# # # # #             f"{cai[j]:>+11.4f} "
# # # # #             f"{shap[j]:>+12.4f} "
# # # # #             f"{diff:>+12.4f} "
# # # # #             f"{flag:>7}"
# # # # #         )

# # # # #     _line(width=78)

# # # # #     # ============================================================
# # # # #     # BIAS SUMMARY
# # # # #     # ============================================================

# # # # #     n_biased = int(
# # # # #         np.sum(
# # # # #             np.abs(difference)
# # # # #             > bias_threshold
# # # # #         )
# # # # #     )

# # # # #     print(
# # # # #         f"\nPotential observational discrepancy "
# # # # #         f"(|CAI − SHAP| > {bias_threshold:.2f})"
# # # # #     )

# # # # #     print(
# # # # #         f"  {n_biased}/{len(cai)} features"
# # # # #     )

# # # # #     # ============================================================
# # # # #     # LARGEST DISAGREEMENT
# # # # #     # ============================================================

# # # # #     if len(order):

# # # # #         largest = int(
# # # # #             order[0]
# # # # #         )

# # # # #         print(
# # # # #             "\nLargest disagreement"
# # # # #         )

# # # # #         _line()

# # # # #         print(
# # # # #             f"  Feature    : "
# # # # #             f"{names[largest]}"
# # # # #         )

# # # # #         print(
# # # # #             f"  CAI        : "
# # # # #             f"{cai[largest]:+.4f}"
# # # # #         )

# # # # #         print(
# # # # #             f"  SHAP       : "
# # # # #             f"{shap[largest]:+.4f}"
# # # # #         )

# # # # #         print(
# # # # #             f"  Difference : "
# # # # #             f"{difference[largest]:+.4f}"
# # # # #         )

# # # # #     print()
# # # # # # ================================================================
# # # # # # 5. FIT DISPLAY
# # # # # # ================================================================


# # # # # def show_fit(
# # # # #     model,
# # # # #     feature_names=None,
# # # # #     verbose=False,
# # # # # ):
# # # # #     """
# # # # #     Compact user-facing model-fit display.

# # # # #     Shows:

# # # # #         - model status
# # # # #         - causal structure
# # # # #         - root/sink variables
# # # # #         - causal graph
# # # # #         - optional ANM mechanism diagnostics
# # # # #     """

# # # # #     _header(
# # # # #         "CAUSE-XAI — MODEL READY"
# # # # #     )

# # # # #     print("\nModel status")
# # # # #     _line()

# # # # #     print(
# # # # #         "  ✓ Causal structure discovered"
# # # # #     )

# # # # #     print(
# # # # #         "  ✓ Causal mechanisms fitted"
# # # # #     )

# # # # #     print(
# # # # #         "  ✓ Model ready for explanation"
# # # # #     )

# # # # #     # ============================================================
# # # # #     # Causal structure
# # # # #     # ============================================================

# # # # #     adj = getattr(
# # # # #         model,
# # # # #         "_adj",
# # # # #         None,
# # # # #     )

# # # # #     if adj is None:

# # # # #         adj = getattr(
# # # # #             model,
# # # # #             "adj_",
# # # # #             None,
# # # # #         )

# # # # #     if adj is not None:

# # # # #         adj = np.asarray(
# # # # #             adj
# # # # #         )

# # # # #         p = adj.shape[0]

# # # # #         names = (
# # # # #             list(feature_names)
# # # # #             if feature_names is not None
# # # # #             else getattr(
# # # # #                 model,
# # # # #                 "feature_names",
# # # # #                 None,
# # # # #             )
# # # # #         )

# # # # #         if names is None:

# # # # #             names = [
# # # # #                 f"X{i + 1}"
# # # # #                 for i in range(p)
# # # # #             ]

# # # # #         # --------------------------------------------------------
# # # # #         # Edges
# # # # #         # --------------------------------------------------------

# # # # #         edges = []

# # # # #         for i in range(p):

# # # # #             for j in range(p):

# # # # #                 if adj[i, j] != 0:

# # # # #                     edges.append(
# # # # #                         (
# # # # #                             i,
# # # # #                             j,
# # # # #                             names[i],
# # # # #                             names[j],
# # # # #                         )
# # # # #                     )

# # # # #         # --------------------------------------------------------
# # # # #         # Parents / children
# # # # #         # --------------------------------------------------------

# # # # #         parents = {
# # # # #             j: []
# # # # #             for j in range(p)
# # # # #         }

# # # # #         children = {
# # # # #             i: []
# # # # #             for i in range(p)
# # # # #         }

# # # # #         for i, j, _, _ in edges:

# # # # #             parents[j].append(i)
# # # # #             children[i].append(j)

# # # # #         root_nodes = [
# # # # #             names[i]
# # # # #             for i in range(p)
# # # # #             if len(parents[i]) == 0
# # # # #         ]

# # # # #         sink_nodes = [
# # # # #             names[i]
# # # # #             for i in range(p)
# # # # #             if len(children[i]) == 0
# # # # #         ]

# # # # #         # --------------------------------------------------------
# # # # #         # Summary
# # # # #         # --------------------------------------------------------

# # # # #         print(
# # # # #             "\nCausal structure"
# # # # #         )

# # # # #         _line()

# # # # #         print(
# # # # #             f"  Variables                : "
# # # # #             f"{p}"
# # # # #         )

# # # # #         print(
# # # # #             f"  Relationships discovered : "
# # # # #             f"{len(edges)}"
# # # # #         )

# # # # #         print(
# # # # #             f"  Root variables           : "
# # # # #             f"{len(root_nodes)}"
# # # # #         )

# # # # #         print(
# # # # #             f"  Sink variables           : "
# # # # #             f"{len(sink_nodes)}"
# # # # #         )

# # # # #         print(
# # # # #             "  DAG valid                : Yes"
# # # # #         )

# # # # #         print(
# # # # #             f"  Root nodes               : "
# # # # #             f"{', '.join(root_nodes)}"
# # # # #         )

# # # # #         print(
# # # # #             f"  Sink nodes               : "
# # # # #             f"{', '.join(sink_nodes)}"
# # # # #         )

# # # # #         # --------------------------------------------------------
# # # # #         # Graph
# # # # #         # --------------------------------------------------------

# # # # #         try:

# # # # #             dag = show_dag(
# # # # #                 model,
# # # # #                 feature_names=names,
# # # # #             )

# # # # #             if dag is not None:

# # # # #                 output_path = dag.render(
# # # # #                     "cause_xai_dag",
# # # # #                     format="png",
# # # # #                     cleanup=True,
# # # # #                 )

# # # # #                 print(
# # # # #                     "\nCausal graph"
# # # # #                 )

# # # # #                 _line()

# # # # #                 print(
# # # # #                     f"  DAG saved to: "
# # # # #                     f"{output_path}"
# # # # #                 )

# # # # #         except Exception as exc:

# # # # #             print(
# # # # #                 "\nCausal graph"
# # # # #             )

# # # # #             _line()

# # # # #             print(
# # # # #                 f"  Graph unavailable: "
# # # # #                 f"{exc}"
# # # # #             )

# # # # #     # ============================================================
# # # # #     # ANM diagnostics
# # # # #     # ============================================================

# # # # #     if verbose:

# # # # #         anm = getattr(
# # # # #             model,
# # # # #             "anm_",
# # # # #             None,
# # # # #         )

# # # # #         if anm is not None:

# # # # #             print(
# # # # #                 "\nCausal mechanism fit"
# # # # #             )

# # # # #             _line()

# # # # #             print(
# # # # #                 f"  {'Variable':<15}"
# # # # #                 f"{'Parents':<25}"
# # # # #                 f"{'Noise':<40}"
# # # # #                 f"{'Residual std':>15}"
# # # # #             )

# # # # #             print(
# # # # #                 "  "
# # # # #                 + "─" * 95
# # # # #             )

# # # # #             residual_std = getattr(
# # # # #                 anm,
# # # # #                 "residual_std",
# # # # #                 {},
# # # # #             )

# # # # #             noise = getattr(
# # # # #                 anm,
# # # # #                 "noise",
# # # # #                 {},
# # # # #             )

# # # # #             eqs = getattr(
# # # # #                 anm,
# # # # #                 "eqs",
# # # # #                 {},
# # # # #             )

# # # # #             for j in anm.order:

# # # # #                 # ------------------------------------------------
# # # # #                 # Variable name
# # # # #                 # ------------------------------------------------

# # # # #                 if (
# # # # #                     feature_names is not None
# # # # #                     and j < len(feature_names)
# # # # #                 ):

# # # # #                     variable = (
# # # # #                         feature_names[j]
# # # # #                     )

# # # # #                 elif (
# # # # #                     getattr(
# # # # #                         anm,
# # # # #                         "feature_names",
# # # # #                         None,
# # # # #                     ) is not None
# # # # #                     and j < len(
# # # # #                         anm.feature_names
# # # # #                     )
# # # # #                 ):

# # # # #                     variable = (
# # # # #                         anm.feature_names[j]
# # # # #                     )

# # # # #                 else:

# # # # #                     variable = (
# # # # #                         f"X{j + 1}"
# # # # #                     )

# # # # #                 # ------------------------------------------------
# # # # #                 # Parents
# # # # #                 # ------------------------------------------------

# # # # #                 eq = eqs.get(j)

# # # # #                 if eq is None:

# # # # #                     parent_names = []

# # # # #                 else:

# # # # #                     parent_names = []

# # # # #                     for p_idx in eq.parents:

# # # # #                         if (
# # # # #                             feature_names is not None
# # # # #                             and p_idx
# # # # #                             < len(feature_names)
# # # # #                         ):

# # # # #                             parent_names.append(
# # # # #                                 feature_names[
# # # # #                                     p_idx
# # # # #                                 ]
# # # # #                             )

# # # # #                         elif (
# # # # #                             getattr(
# # # # #                                 anm,
# # # # #                                 "feature_names",
# # # # #                                 None,
# # # # #                             ) is not None
# # # # #                             and p_idx
# # # # #                             < len(
# # # # #                                 anm.feature_names
# # # # #                             )
# # # # #                         ):

# # # # #                             parent_names.append(
# # # # #                                 anm.feature_names[
# # # # #                                     p_idx
# # # # #                                 ]
# # # # #                             )

# # # # #                         else:

# # # # #                             parent_names.append(
# # # # #                                 f"X{p_idx + 1}"
# # # # #                             )

# # # # #                 parents_text = (
# # # # #                     "["
# # # # #                     + ", ".join(
# # # # #                         parent_names
# # # # #                     )
# # # # #                     + "]"
# # # # #                 )

# # # # #                 # ------------------------------------------------
# # # # #                 # Noise
# # # # #                 # ------------------------------------------------

# # # # #                 try:

# # # # #                     loc, scale = noise[j]

# # # # #                     noise_text = (
# # # # #                         f"Laplace("
# # # # #                         f"loc={loc:.3f}, "
# # # # #                         f"scale={scale:.3f})"
# # # # #                     )

# # # # #                 except Exception:

# # # # #                     noise_text = "N/A"

# # # # #                 # ------------------------------------------------
# # # # #                 # Residual std
# # # # #                 # ------------------------------------------------

# # # # #                 std = residual_std.get(
# # # # #                     j,
# # # # #                     np.nan,
# # # # #                 )

# # # # #                 print(
# # # # #                     f"  {variable:<15}"
# # # # #                     f"{parents_text:<25}"
# # # # #                     f"{noise_text:<40}"
# # # # #                     f"{std:>15.3f}"
# # # # #                 )

# # # # #     print()


# # # # # # ================================================================
# # # # # # 6. DAG DISPLAY
# # # # # # ================================================================


# # # # # def show_dag(
# # # # #     model,
# # # # #     feature_names=None,
# # # # # ):
# # # # #     """
# # # # #     Create a Graphviz representation of the learned DAG.

# # # # #     Returns
# # # # #     -------
# # # # #     graphviz.Digraph or None
# # # # #     """

# # # # #     try:

# # # # #         from graphviz import Digraph

# # # # #     except ImportError:

# # # # #         print(
# # # # #             "DAG visualization requires Graphviz."
# # # # #         )

# # # # #         print(
# # # # #             "Install the Python package with:"
# # # # #         )

# # # # #         print(
# # # # #             "  pip install graphviz"
# # # # #         )

# # # # #         return None

# # # # #     adj = np.asarray(
# # # # #         model._adj
# # # # #     )

# # # # #     p = adj.shape[0]

# # # # #     if feature_names is not None:

# # # # #         names = list(
# # # # #             feature_names
# # # # #         )

# # # # #     else:

# # # # #         names = [
# # # # #             f"X{i + 1}"
# # # # #             for i in range(p)
# # # # #         ]

# # # # #     dot = Digraph(
# # # # #         "CAUSE_XAI_DAG"
# # # # #     )

# # # # #     # ------------------------------------------------------------
# # # # #     # Layout
# # # # #     # ------------------------------------------------------------

# # # # #     dot.attr(
# # # # #         rankdir="LR",
# # # # #         splines="ortho",
# # # # #         nodesep="0.45",
# # # # #         ranksep="0.8",
# # # # #         bgcolor="white",
# # # # #     )

# # # # #     dot.attr(
# # # # #         "node",
# # # # #         shape="box",
# # # # #         style="rounded",
# # # # #         fontsize="11",
# # # # #         margin="0.12",
# # # # #     )

# # # # #     dot.attr(
# # # # #         "edge",
# # # # #         arrowsize="0.7",
# # # # #         penwidth="1.2",
# # # # #     )

# # # # #     # ------------------------------------------------------------
# # # # #     # Nodes
# # # # #     # ------------------------------------------------------------

# # # # #     for i, name in enumerate(names):

# # # # #         has_parent = np.any(
# # # # #             adj[:, i]
# # # # #         )

# # # # #         has_child = np.any(
# # # # #             adj[i, :]
# # # # #         )

# # # # #         if not has_parent:

# # # # #             label = (
# # # # #                 f"{name}\n(root)"
# # # # #             )

# # # # #         elif not has_child:

# # # # #             label = (
# # # # #                 f"{name}\n(sink)"
# # # # #             )

# # # # #         else:

# # # # #             label = name

# # # # #         dot.node(
# # # # #             str(i),
# # # # #             label,
# # # # #         )

# # # # #     # ------------------------------------------------------------
# # # # #     # Edges
# # # # #     # ------------------------------------------------------------

# # # # #     for i in range(p):

# # # # #         for j in range(p):

# # # # #             if adj[i, j] != 0:

# # # # #                 dot.edge(
# # # # #                     str(i),
# # # # #                     str(j),
# # # # #                 )

# # # # #     return dot


# # # # # # ================================================================
# # # # # # 7. GENERIC DISPLAY
# # # # # # ================================================================


# # # # # def display(
# # # # #     result,
# # # # #     feature_names=None,
# # # # #     task="regression",
# # # # # ):
# # # # #     """
# # # # #     Automatically select the appropriate user-facing display.

# # # # #     Supported result types:

# # # # #         UnifiedExplanation
# # # # #         CCEResult
# # # # #         CAIResult
# # # # #         CAI-vs-SHAP comparison dictionary
# # # # #     """

# # # # #     # ------------------------------------------------------------
# # # # #     # Unified explanation
# # # # #     # ------------------------------------------------------------

# # # # #     if isinstance(
# # # # #         result,
# # # # #         UnifiedExplanation,
# # # # #     ):

# # # # #         return show_explanation(
# # # # #             result,
# # # # #             feature_names=feature_names,
# # # # #             task=task,
# # # # #         )

# # # # #     # ------------------------------------------------------------
# # # # #     # Counterfactual
# # # # #     # ------------------------------------------------------------

# # # # #     elif isinstance(
# # # # #         result,
# # # # #         CCEResult,
# # # # #     ):

# # # # #         return show_counterfactual(
# # # # #             result,
# # # # #             feature_names=feature_names,
# # # # #             task=task,
# # # # #         )

# # # # #     # ------------------------------------------------------------
# # # # #     # CAI
# # # # #     # ------------------------------------------------------------

# # # # #     elif isinstance(
# # # # #         result,
# # # # #         CAIResult,
# # # # #     ):

# # # # #         return show_attribution(
# # # # #             result,
# # # # #             feature_names=feature_names,
# # # # #             task=task,
# # # # #         )

# # # # #     # ------------------------------------------------------------
# # # # #     # CAI vs SHAP
# # # # #     # ------------------------------------------------------------

# # # # #     elif isinstance(
# # # # #         result,
# # # # #         dict,
# # # # #     ):

# # # # #         if (
# # # # #             "cai" in result
# # # # #             and "shap_style" in result
# # # # #         ):

# # # # #             return show_cai_vs_shap(
# # # # #                 result,
# # # # #                 feature_names=feature_names,
# # # # #             )

# # # # #         raise TypeError(
# # # # #             "Dictionary does not contain a recognised "
# # # # #             "CAUSE-XAI result."
# # # # #         )

# # # # #     # ------------------------------------------------------------
# # # # #     # Unsupported
# # # # #     # ------------------------------------------------------------

# # # # #     else:

# # # # #         raise TypeError(
# # # # #             f"Unsupported result type: "
# # # # #             f"{type(result).__name__}"
# # # # #         )


# # # # # # ================================================================
# # # # # # PUBLIC API
# # # # # # ================================================================


# # # # # __all__ = [
# # # # #     "show_fit",
# # # # #     "show_dag",
# # # # #     "show_counterfactual",
# # # # #     "show_attribution",
# # # # #     "show_explanation",
# # # # #     "show_cai_vs_shap",
# # # # #     "display",
# # # # # ]

# # # # """
# # # # User-facing display layer for CAUSE-XAI.

# # # # The display layer converts CAUSE-XAI results into
# # # # human-readable tables, charts, and explanations.

# # # # Public functions
# # # # ----------------
# # # # show_fit()
# # # # show_counterfactual()
# # # # show_attribution()
# # # # show_explanation()
# # # # show_cai_vs_shap()
# # # # display()

# # # # Important
# # # # ---------
# # # # This module does not require a task/classification/regression
# # # # argument. It displays the numerical outputs produced by the
# # # # CAUSE-XAI methods directly.
# # # # """

# # # # import numpy as np

# # # # from .results import (
# # # #     CCEResult,
# # # #     CAIResult,
# # # #     UnifiedExplanation,
# # # # )


# # # # # ================================================================
# # # # # OPTIONAL VISUALIZATION DEPENDENCY
# # # # # ================================================================

# # # # def _get_plt():
# # # #     """
# # # #     Import matplotlib only when a graphical display is requested.
# # # #     """
# # # #     try:
# # # #         import matplotlib.pyplot as plt
# # # #         return plt
# # # #     except ImportError as exc:
# # # #         raise ImportError(
# # # #             "CAUSE-XAI graphical displays require matplotlib.\n"
# # # #             "Install it with:\n"
# # # #             "    pip install matplotlib"
# # # #         ) from exc


# # # # # ================================================================
# # # # # BASIC HELPERS
# # # # # ================================================================

# # # # def _names(values, feature_names=None):
# # # #     """Return readable feature names."""

# # # #     n = len(values)

# # # #     if feature_names is not None:

# # # #         if len(feature_names) != n:
# # # #             raise ValueError(
# # # #                 "feature_names must have the same length "
# # # #                 "as the number of features."
# # # #             )

# # # #         return list(feature_names)

# # # #     return [
# # # #         f"Feature {i + 1}"
# # # #         for i in range(n)
# # # #     ]


# # # # def _line(char="─", width=78):
# # # #     print(char * width)


# # # # def _header(title, width=78):
# # # #     print()
# # # #     print("═" * width)
# # # #     print(title.center(width))
# # # #     print("═" * width)


# # # # def _format_change(old, new):
# # # #     """
# # # #     Convert a numerical change into readable language.
# # # #     """

# # # #     delta = float(new) - float(old)

# # # #     if abs(delta) < 1e-10:
# # # #         return "No change"

# # # #     if delta > 0:
# # # #         return f"Increase by {abs(delta):.3f}"

# # # #     return f"Decrease by {abs(delta):.3f}"


# # # # def _format_ci(ci):
# # # #     """Format a confidence interval."""

# # # #     return (
# # # #         f"[{float(ci[0]):+.4f}, "
# # # #         f"{float(ci[1]):+.4f}]"
# # # #     )


# # # # def _effect_description(effect):
# # # #     """
# # # #     Human-readable CAI interpretation.

# # # #     This remains intentionally generic because the
# # # #     underlying model output may be a probability or
# # # #     a regression value.
# # # #     """

# # # #     effect = float(effect)

# # # #     if abs(effect) < 1e-10:
# # # #         return "Little measurable influence"

# # # #     magnitude = abs(effect)

# # # #     if effect > 0:

# # # #         if magnitude >= 0.20:
# # # #             return "Strong increase"

# # # #         if magnitude >= 0.10:
# # # #             return "Moderate increase"

# # # #         return "Small increase"

# # # #     if magnitude >= 0.20:
# # # #         return "Strong decrease"

# # # #     if magnitude >= 0.10:
# # # #         return "Moderate decrease"

# # # #     return "Small decrease"


# # # # def _direction_sentence(feature, effect):
# # # #     """Natural-language causal direction."""

# # # #     effect = float(effect)

# # # #     if effect > 0:

# # # #         return (
# # # #             f"{feature} has the strongest estimated causal "
# # # #             f"influence and increases the expected model output."
# # # #         )

# # # #     if effect < 0:

# # # #         return (
# # # #             f"{feature} has the strongest estimated causal "
# # # #             f"influence and decreases the expected model output."
# # # #         )

# # # #     return (
# # # #         f"{feature} has little measurable causal influence "
# # # #         f"on the expected model output."
# # # #     )


# # # # def _safe_float(value):
# # # #     """Convert scalar-like value to float."""

# # # #     try:
# # # #         return float(value)
# # # #     except Exception:
# # # #         return value


# # # # # ================================================================
# # # # # GRAPHICAL TABLE HELPER
# # # # # ================================================================

# # # # def _show_table(
# # # #     rows,
# # # #     columns,
# # # #     title=None,
# # # #     figsize=None,
# # # #     font_size=9,
# # # # ):
# # # #     """
# # # #     Display an actual matplotlib table.

# # # #     Parameters
# # # #     ----------
# # # #     rows : list[list]
# # # #         Table rows.
# # # #     columns : list[str]
# # # #         Column headings.
# # # #     """

# # # #     plt = _get_plt()

# # # #     if figsize is None:

# # # #         width = max(
# # # #             9,
# # # #             len(columns) * 1.5,
# # # #         )

# # # #         height = max(
# # # #             2.5,
# # # #             min(14, 1.0 + 0.42 * len(rows)),
# # # #         )

# # # #         figsize = (
# # # #             width,
# # # #             height,
# # # #         )

# # # #     fig, ax = plt.subplots(
# # # #         figsize=figsize
# # # #     )

# # # #     ax.axis("off")

# # # #     if title is not None:
# # # #         ax.set_title(
# # # #             title,
# # # #             fontsize=13,
# # # #             pad=16,
# # # #             fontweight="bold",
# # # #         )

# # # #     table = ax.table(
# # # #         cellText=rows,
# # # #         colLabels=columns,
# # # #         loc="center",
# # # #         cellLoc="center",
# # # #     )

# # # #     table.auto_set_font_size(False)
# # # #     table.set_fontsize(font_size)
# # # #     table.scale(
# # # #         1,
# # # #         1.6,
# # # #     )

# # # #     plt.tight_layout()
# # # #     plt.show()

# # # #     return fig


# # # # # ================================================================
# # # # # METRIC CARD DISPLAY
# # # # # ================================================================

# # # # def _show_metric_cards(metrics):
# # # #     """
# # # #     Display causal metrics as a compact visual dashboard.

# # # #     metrics:
# # # #         list of dictionaries with:
# # # #             title
# # # #             value
# # # #             explanation
# # # #     """

# # # #     plt = _get_plt()

# # # #     n = len(metrics)

# # # #     cols = 3
# # # #     rows = int(
# # # #         np.ceil(n / cols)
# # # #     )

# # # #     fig = plt.figure(
# # # #         figsize=(
# # # #             13,
# # # #             3.0 * rows,
# # # #         )
# # # #     )

# # # #     for i, metric in enumerate(metrics):

# # # #         ax = fig.add_subplot(
# # # #             rows,
# # # #             cols,
# # # #             i + 1,
# # # #         )

# # # #         ax.axis("off")

# # # #         title = metric["title"]
# # # #         value = metric["value"]
# # # #         explanation = metric["explanation"]

# # # #         ax.text(
# # # #             0.5,
# # # #             0.76,
# # # #             title,
# # # #             ha="center",
# # # #             va="center",
# # # #             fontsize=10,
# # # #             fontweight="bold",
# # # #         )

# # # #         ax.text(
# # # #             0.5,
# # # #             0.50,
# # # #             value,
# # # #             ha="center",
# # # #             va="center",
# # # #             fontsize=22,
# # # #             fontweight="bold",
# # # #         )

# # # #         ax.text(
# # # #             0.5,
# # # #             0.19,
# # # #             explanation,
# # # #             ha="center",
# # # #             va="center",
# # # #             fontsize=8.5,
# # # #             wrap=True,
# # # #         )

# # # #         for spine in ax.spines.values():
# # # #             spine.set_visible(True)

# # # #     # Hide unused axes.

# # # #     total = rows * cols

# # # #     for i in range(n, total):

# # # #         ax = fig.add_subplot(
# # # #             rows,
# # # #             cols,
# # # #             i + 1,
# # # #         )

# # # #         ax.axis("off")

# # # #     plt.tight_layout()
# # # #     plt.show()

# # # #     return fig


# # # # # ================================================================
# # # # # PREDICTION TRANSITION VISUAL
# # # # # ================================================================

# # # # def _show_prediction_transition(
# # # #     current,
# # # #     achieved,
# # # #     target=None,
# # # #     title="Prediction change",
# # # # ):
# # # #     """
# # # #     Show the movement from current model output
# # # #     to the achieved counterfactual output.
# # # #     """

# # # #     plt = _get_plt()

# # # #     current = float(current)
# # # #     achieved = float(achieved)

# # # #     fig, ax = plt.subplots(
# # # #         figsize=(11, 3.8)
# # # #     )

# # # #     minimum = min(
# # # #         current,
# # # #         achieved,
# # # #     )

# # # #     maximum = max(
# # # #         current,
# # # #         achieved,
# # # #     )

# # # #     span = max(
# # # #         abs(maximum - minimum),
# # # #         1e-6,
# # # #     )

# # # #     left = minimum - 0.15 * span
# # # #     right = maximum + 0.15 * span

# # # #     ax.set_xlim(
# # # #         left,
# # # #         right,
# # # #     )

# # # #     ax.set_ylim(
# # # #         -0.8,
# # # #         0.8,
# # # #     )

# # # #     ax.axhline(
# # # #         0,
# # # #         linewidth=2,
# # # #     )

# # # #     ax.scatter(
# # # #         [current],
# # # #         [0],
# # # #         s=120,
# # # #         zorder=5,
# # # #     )

# # # #     ax.scatter(
# # # #         [achieved],
# # # #         [0],
# # # #         s=120,
# # # #         zorder=5,
# # # #     )

# # # #     ax.annotate(
# # # #         f"Current\n{current:.4f}",
# # # #         xy=(current, 0),
# # # #         xytext=(current, 0.45),
# # # #         ha="center",
# # # #         arrowprops=dict(
# # # #             arrowstyle="->",
# # # #         ),
# # # #     )

# # # #     ax.annotate(
# # # #         f"After change\n{achieved:.4f}",
# # # #         xy=(achieved, 0),
# # # #         xytext=(achieved, -0.50),
# # # #         ha="center",
# # # #         arrowprops=dict(
# # # #             arrowstyle="->",
# # # #         ),
# # # #     )

# # # #     ax.annotate(
# # # #         "",
# # # #         xy=(achieved, 0),
# # # #         xytext=(current, 0),
# # # #         arrowprops=dict(
# # # #             arrowstyle="<->",
# # # #             linewidth=2,
# # # #         ),
# # # #     )

# # # #     delta = achieved - current

# # # #     midpoint = (
# # # #         current + achieved
# # # #     ) / 2

# # # #     ax.text(
# # # #         midpoint,
# # # #         0.13,
# # # #         f"Change: {delta:+.4f}",
# # # #         ha="center",
# # # #         fontsize=10,
# # # #         fontweight="bold",
# # # #     )

# # # #     if target is not None:

# # # #         ax.axvline(
# # # #             float(target),
# # # #             linestyle="--",
# # # #             linewidth=1.5,
# # # #         )

# # # #         ax.text(
# # # #             float(target),
# # # #             0.68,
# # # #             f"Target\n{float(target):.4f}",
# # # #             ha="center",
# # # #             fontsize=8,
# # # #         )

# # # #     ax.set_title(
# # # #         title,
# # # #         fontsize=13,
# # # #         fontweight="bold",
# # # #     )

# # # #     ax.set_yticks([])

# # # #     ax.set_xlabel(
# # # #         "Model output"
# # # #     )

# # # #     plt.tight_layout()
# # # #     plt.show()

# # # #     return fig


# # # # # ================================================================
# # # # # 1. COUNTERFACTUAL DISPLAY
# # # # # ================================================================

# # # # def show_counterfactual(
# # # #     result: CCEResult,
# # # #     feature_names=None,
# # # # ):
# # # #     """
# # # #     Display a user-facing causal counterfactual.

# # # #     Shows:

# # # #         1. Prediction transition
# # # #         2. Causal metric cards
# # # #         3. Direct interventions
# # # #         4. Downstream effects
# # # #         5. Technical counterfactual table
# # # #     """

# # # #     names = _names(
# # # #         result.x_obs,
# # # #         feature_names,
# # # #     )

# # # #     _header(
# # # #         "COUNTERFACTUAL EXPLANATION"
# # # #     )

# # # #     # ============================================================
# # # #     # 1. Prediction summary
# # # #     # ============================================================

# # # #     print("\nWHAT WOULD NEED TO CHANGE?")
# # # #     _line()

# # # #     print(
# # # #         f"  Current model output : "
# # # #         f"{result.y_fact:.4f}"
# # # #     )

# # # #     print(
# # # #         f"  Requested target     : "
# # # #         f"{result.y_foil:.4f}"
# # # #     )

# # # #     print(
# # # #         f"  Achieved output      : "
# # # #         f"{result.y_achieved:.4f}"
# # # #     )

# # # #     if result.feasible:

# # # #         print(
# # # #             "\n  ✓ A feasible counterfactual was found."
# # # #         )

# # # #     else:

# # # #         print(
# # # #             "\n  ✗ The requested target was not reached."
# # # #         )

# # # #     # Graphical prediction transition.

# # # #     _show_prediction_transition(
# # # #         result.y_fact,
# # # #         result.y_achieved,
# # # #         target=result.y_foil,
# # # #         title="Counterfactual prediction change",
# # # #     )

# # # #     # ============================================================
# # # #     # 2. Causal metrics
# # # #     # ============================================================

# # # #     direct = (
# # # #         result.direct_interventions
# # # #         or []
# # # #     )

# # # #     changed = (
# # # #         result.changed
# # # #         or []
# # # #     )

# # # #     downstream = [
# # # #         j
# # # #         for j in changed
# # # #         if j not in direct
# # # #     ]

# # # #     total_features = len(
# # # #         result.x_obs
# # # #     )

# # # #     direct_count = len(
# # # #         direct
# # # #     )

# # # #     downstream_count = len(
# # # #         downstream
# # # #     )

# # # #     sparsity = float(
# # # #         result.sparsity
# # # #     )

# # # #     violation = float(
# # # #         result.violation
# # # #     )

# # # #     distance = float(
# # # #         result.d_causal
# # # #     )

# # # #     violation_ok = (
# # # #         violation < 1.5
# # # #     )

# # # #     metrics = [

# # # #         {
# # # #             "title": "DIRECT INTERVENTIONS",
# # # #             "value": f"{direct_count} / {total_features}",
# # # #             "explanation": (
# # # #                 "Features intentionally changed\n"
# # # #                 "to obtain the counterfactual."
# # # #             ),
# # # #         },

# # # #         {
# # # #             "title": "DOWNSTREAM CHANGES",
# # # #             "value": str(downstream_count),
# # # #             "explanation": (
# # # #                 "Additional features that changed\n"
# # # #                 "because of causal propagation."
# # # #             ),
# # # #         },

# # # #         {
# # # #             "title": "CAUSAL SPARSITY",
# # # #             "value": f"{sparsity * 100:.1f}%",
# # # #             "explanation": (
# # # #                 "How concentrated the solution is.\n"
# # # #                 "Higher means fewer direct changes."
# # # #             ),
# # # #         },

# # # #         {
# # # #             "title": "CAUSAL CONSISTENCY",
# # # #             "value": (
# # # #                 "✓ Consistent"
# # # #                 if violation_ok
# # # #                 else "⚠ Check"
# # # #             ),
# # # #             "explanation": (
# # # #                 f"Constraint score: {violation:.4f}\n"
# # # #                 "Lower indicates better consistency."
# # # #             ),
# # # #         },

# # # #         {
# # # #             "title": "CAUSAL DISTANCE",
# # # #             "value": f"{distance:.4f}",
# # # #             "explanation": (
# # # #                 "Distance of the counterfactual\n"
# # # #                 "from the observed causal state."
# # # #             ),
# # # #         },

# # # #         {
# # # #             "title": "RUNTIME",
# # # #             "value": f"{float(result.runtime):.2f} s",
# # # #             "explanation": (
# # # #                 "Time required to find\n"
# # # #                 "the counterfactual."
# # # #             ),
# # # #         },
# # # #     ]

# # # #     _show_metric_cards(
# # # #         metrics
# # # #     )

# # # #     # ============================================================
# # # #     # 3. Direct interventions
# # # #     # ============================================================

# # # #     print("\nDIRECT INTERVENTIONS")
# # # #     _line()

# # # #     if direct:

# # # #         rows = []

# # # #         for j in direct:

# # # #             old = float(
# # # #                 result.x_obs[j]
# # # #             )

# # # #             new = float(
# # # #                 result.x_star[j]
# # # #             )

# # # #             delta = new - old

# # # #             rows.append(
# # # #                 [
# # # #                     names[j],
# # # #                     f"{old:.4f}",
# # # #                     f"{new:.4f}",
# # # #                     f"{delta:+.4f}",
# # # #                     _format_change(
# # # #                         old,
# # # #                         new,
# # # #                     ),
# # # #                 ]
# # # #             )

# # # #         _show_table(
# # # #             rows,
# # # #             [
# # # #                 "Feature",
# # # #                 "Current",
# # # #                 "New value",
# # # #                 "Change",
# # # #                 "Required action",
# # # #             ],
# # # #             title="Direct causal interventions",
# # # #         )

# # # #     else:

# # # #         print(
# # # #             "  No direct feature intervention."
# # # #         )

# # # #     # ============================================================
# # # #     # 4. Downstream changes
# # # #     # ============================================================

# # # #     print("\nDOWNSTREAM EFFECTS")
# # # #     _line()

# # # #     if downstream:

# # # #         print(
# # # #             f"  {downstream_count} feature(s) changed "
# # # #             "as a consequence of the direct intervention."
# # # #         )

# # # #         rows = []

# # # #         for j in downstream:

# # # #             old = float(
# # # #                 result.x_obs[j]
# # # #             )

# # # #             new = float(
# # # #                 result.x_star[j]
# # # #             )

# # # #             delta = new - old

# # # #             rows.append(
# # # #                 [
# # # #                     names[j],
# # # #                     f"{old:.4f}",
# # # #                     f"{new:.4f}",
# # # #                     f"{delta:+.4f}",
# # # #                 ]
# # # #             )

# # # #         _show_table(
# # # #             rows,
# # # #             [
# # # #                 "Feature",
# # # #                 "Original",
# # # #                 "Causal result",
# # # #                 "Change",
# # # #             ],
# # # #             title="Downstream causal changes",
# # # #         )

# # # #     else:

# # # #         print(
# # # #             "  No downstream feature changes."
# # # #         )

# # # #     # ============================================================
# # # #     # 5. Complete technical table
# # # #     # ============================================================

# # # #     print("\nCOUNTERFACTUAL DETAILS")
# # # #     _line()

# # # #     rows = []

# # # #     for j in changed:

# # # #         old = float(
# # # #             result.x_obs[j]
# # # #         )

# # # #         new = float(
# # # #             result.x_star[j]
# # # #         )

# # # #         role = (
# # # #             "Direct intervention"
# # # #             if j in direct
# # # #             else "Downstream"
# # # #         )

# # # #         rows.append(
# # # #             [
# # # #                 names[j],
# # # #                 f"{old:.4f}",
# # # #                 f"{new:.4f}",
# # # #                 f"{new - old:+.4f}",
# # # #                 role,
# # # #             ]
# # # #         )

# # # #     if rows:

# # # #         _show_table(
# # # #             rows,
# # # #             [
# # # #                 "Feature",
# # # #                 "Original",
# # # #                 "Counterfactual",
# # # #                 "Δ",
# # # #                 "Causal role",
# # # #             ],
# # # #             title="All changed features",
# # # #         )

# # # #     print()


# # # # # ================================================================
# # # # # 2. CAUSAL FEATURE IMPACT / CAI
# # # # # ================================================================

# # # # def show_attribution(
# # # #     result: CAIResult,
# # # #     feature_names=None,
# # # # ):
# # # #     """
# # # #     Display CAI attribution.

# # # #     This section intentionally remains focused on
# # # #     the CAI attribution representation.

# # # #     The display provides:
# # # #         - CAI ranking
# # # #         - technical uncertainty
# # # #         - main causal driver
# # # #         - baseline reference
# # # #     """

# # # #     names = _names(
# # # #         result.x_obs,
# # # #         feature_names,
# # # #     )

# # # #     cai = np.asarray(
# # # #         result.cai,
# # # #         dtype=float,
# # # #     )

# # # #     if cai.size == 0:

# # # #         _header(
# # # #             "CAUSAL FEATURE IMPACT"
# # # #         )

# # # #         print(
# # # #             "\n  No CAI values available."
# # # #         )

# # # #         return

# # # #     order = np.argsort(
# # # #         np.abs(cai)
# # # #     )[::-1]

# # # #     top = int(
# # # #         order[0]
# # # #     )

# # # #     top_effect = float(
# # # #         cai[top]
# # # #     )

# # # #     _header(
# # # #         "CAUSAL FEATURE IMPACT"
# # # #     )

# # # #     print(
# # # #         "\nThe causal effect estimates how intervening "
# # # #         "on each feature changes the expected model output."
# # # #     )

# # # #     if result.n_samples is not None:

# # # #         print(
# # # #             f"\n  Monte Carlo samples : "
# # # #             f"{result.n_samples}"
# # # #         )

# # # #     # ============================================================
# # # #     # CAI table
# # # #     # ============================================================

# # # #     print("\nFeature-level causal effects")
# # # #     _line()

# # # #     rows = []

# # # #     for rank, j in enumerate(order):

# # # #         j = int(j)

# # # #         intervention = None

# # # #         if result.intervention_values is not None:

# # # #             try:
# # # #                 intervention = float(
# # # #                     result.x_obs[j]
# # # #                 )
# # # #             except Exception:
# # # #                 intervention = None

# # # #         f_do = float(
# # # #             result.f_do[j]
# # # #         )

# # # #         effect = float(
# # # #             cai[j]
# # # #         )

# # # #         se = None

# # # #         if result.standard_errors is not None:
# # # #             se = float(
# # # #                 result.standard_errors[j]
# # # #             )

# # # #         ci = None

# # # #         if result.confidence_intervals is not None:
# # # #             ci = _format_ci(
# # # #                 result.confidence_intervals[j]
# # # #             )

# # # #         rows.append(
# # # #             [
# # # #                 rank + 1,
# # # #                 names[j],
# # # #                 (
# # # #                     f"{intervention:.4f}"
# # # #                     if intervention is not None
# # # #                     else "-"
# # # #                 ),
# # # #                 f"{f_do:.4f}",
# # # #                 f"{effect:+.4f}",
# # # #                 (
# # # #                     f"{se:.4f}"
# # # #                     if se is not None
# # # #                     else "-"
# # # #                 ),
# # # #                 ci if ci is not None else "-",
# # # #             ]
# # # #         )

# # # #     _show_table(
# # # #         rows,
# # # #         [
# # # #             "Rank",
# # # #             "Feature",
# # # #             "Intervention",
# # # #             "E[f | do]",
# # # #             "CAI",
# # # #             "SE",
# # # #             "95% CI",
# # # #         ],
# # # #         title="Feature-level causal effects",
# # # #         figsize=(
# # # #             13,
# # # #             max(
# # # #                 4,
# # # #                 min(
# # # #                     16,
# # # #                     1.5 + 0.35 * len(rows),
# # # #                 ),
# # # #             ),
# # # #         ),
# # # #         font_size=8,
# # # #     )

# # # #     # ============================================================
# # # #     # Main driver
# # # #     # ============================================================

# # # #     print("\nMAIN CAUSAL DRIVER")
# # # #     _line()

# # # #     print(
# # # #         f"  {_direction_sentence(names[top], top_effect)}"
# # # #     )

# # # #     print(
# # # #         f"  CAI : {top_effect:+.4f}"
# # # #     )

# # # #     print(
# # # #         f"  Baseline expected output : "
# # # #         f"{result.baseline:.4f}"
# # # #     )

# # # #     print()


# # # # # ================================================================
# # # # # 3. UNIFIED EXPLANATION
# # # # # ================================================================

# # # # def show_explanation(
# # # #     explanation: UnifiedExplanation,
# # # #     feature_names=None,
# # # # ):
# # # #     """
# # # #     Main CAUSE-XAI explanation.

# # # #     The unified display answers:

# # # #         1. What is the model predicting?
# # # #         2. What can change that prediction?
# # # #         3. Which feature is the strongest causal driver?
# # # #         4. What happens downstream?
# # # #         5. Is the counterfactual causally consistent?

# # # #     The CAI visual itself is intentionally kept separate
# # # #     from this high-level dashboard.
# # # #     """

# # # #     names = _names(
# # # #         explanation.x_obs,
# # # #         feature_names,
# # # #     )

# # # #     cce = explanation.cce
# # # #     cai = explanation.cai

# # # #     cai_values = np.asarray(
# # # #         cai.cai,
# # # #         dtype=float,
# # # #     )

# # # #     if cai_values.size == 0:

# # # #         _header(
# # # #             "CAUSE-XAI — MODEL EXPLANATION"
# # # #         )

# # # #         print(
# # # #             "\n  No causal attribution values available."
# # # #         )

# # # #         return

# # # #     order = np.argsort(
# # # #         np.abs(cai_values)
# # # #     )[::-1]

# # # #     _header(
# # # #         "CAUSE-XAI — MODEL EXPLANATION"
# # # #     )

# # # #     # ============================================================
# # # #     # 1. HIGH LEVEL PREDICTION
# # # #     # ============================================================

# # # #     print("\n1. MODEL OUTPUT")
# # # #     _line()

# # # #     print(
# # # #         f"  Current output : "
# # # #         f"{explanation.y_fact:.4f}"
# # # #     )

# # # #     print(
# # # #         f"  Target output  : "
# # # #         f"{explanation.y_foil:.4f}"
# # # #     )

# # # #     print(
# # # #         f"  Achieved output: "
# # # #         f"{cce.y_achieved:.4f}"
# # # #     )

# # # #     if cce.feasible:

# # # #         print(
# # # #             "\n  ✓ A feasible causal counterfactual "
# # # #             "was found."
# # # #         )

# # # #     else:

# # # #         print(
# # # #             "\n  ✗ The requested target could not "
# # # #             "be reached."
# # # #         )

# # # #     _show_prediction_transition(
# # # #         explanation.y_fact,
# # # #         cce.y_achieved,
# # # #         target=explanation.y_foil,
# # # #         title="Model output: current → counterfactual",
# # # #     )

# # # #     # ============================================================
# # # #     # 2. EXPLANATION SUMMARY
# # # #     # ============================================================

# # # #     top = int(
# # # #         order[0]
# # # #     )

# # # #     top_effect = float(
# # # #         cai_values[top]
# # # #     )

# # # #     direct = (
# # # #         cce.direct_interventions
# # # #         or []
# # # #     )

# # # #     changed = (
# # # #         cce.changed
# # # #         or []
# # # #     )

# # # #     downstream = [
# # # #         j
# # # #         for j in changed
# # # #         if j not in direct
# # # #     ]

# # # #     print("\n2. WHAT EXPLAINS THE RESULT?")
# # # #     _line()

# # # #     print(
# # # #         f"  Why does the output move?"
# # # #     )

# # # #     print(
# # # #         f"    {names[top]} is the strongest causal driver "
# # # #         f"with CAI = {top_effect:+.4f}."
# # # #     )

# # # #     print(
# # # #         f"\n  What would need to change?"
# # # #     )

# # # #     if direct:

# # # #         for j in direct:

# # # #             old = float(
# # # #                 cce.x_obs[j]
# # # #             )

# # # #             new = float(
# # # #                 cce.x_star[j]
# # # #             )

# # # #             print(
# # # #                 f"    • {names[j]}: "
# # # #                 f"{old:.4f} → {new:.4f} "
# # # #                 f"({_format_change(old, new).lower()})"
# # # #             )

# # # #     elif changed:

# # # #         print(
# # # #             "    The solution changes "
# # # #             "the following features:"
# # # #         )

# # # #         for j in changed[:5]:

# # # #             old = float(
# # # #                 cce.x_obs[j]
# # # #             )

# # # #             new = float(
# # # #                 cce.x_star[j]
# # # #             )

# # # #             print(
# # # #                 f"    • {names[j]}: "
# # # #                 f"{old:.4f} → {new:.4f}"
# # # #             )

# # # #     else:

# # # #         print(
# # # #             "    No feature change was required."
# # # #         )

# # # #     # ============================================================
# # # #     # 3. CAUSAL METRIC DASHBOARD
# # # #     # ============================================================

# # # #     print("\n3. CAUSAL QUALITY")
# # # #     _line()

# # # #     violation = float(
# # # #         cce.violation
# # # #     )

# # # #     violation_ok = (
# # # #         violation < 1.5
# # # #     )

# # # #     total_features = len(
# # # #         explanation.x_obs
# # # #     )

# # # #     direct_count = len(
# # # #         direct
# # # #     )

# # # #     downstream_count = len(
# # # #         downstream
# # # #     )

# # # #     metrics = [

# # # #         {
# # # #             "title": "DIRECT CHANGES",
# # # #             "value": f"{direct_count} / {total_features}",
# # # #             "explanation": (
# # # #                 "Features deliberately changed\n"
# # # #                 "to obtain the target."
# # # #             ),
# # # #         },

# # # #         {
# # # #             "title": "DOWNSTREAM EFFECTS",
# # # #             "value": str(downstream_count),
# # # #             "explanation": (
# # # #                 "Features that changed because\n"
# # # #                 "of causal propagation."
# # # #             ),
# # # #         },

# # # #         {
# # # #             "title": "CAUSAL SPARSITY",
# # # #             "value": (
# # # #                 f"{float(cce.sparsity) * 100:.1f}%"
# # # #             ),
# # # #             "explanation": (
# # # #                 "Higher means the solution uses\n"
# # # #                 "fewer direct changes."
# # # #             ),
# # # #         },

# # # #         {
# # # #             "title": "CAUSAL CONSISTENCY",
# # # #             "value": (
# # # #                 "✓ Consistent"
# # # #                 if violation_ok
# # # #                 else "⚠ Check"
# # # #             ),
# # # #             "explanation": (
# # # #                 f"Constraint score: {violation:.4f}\n"
# # # #                 "Lower indicates better consistency."
# # # #             ),
# # # #         },

# # # #         {
# # # #             "title": "CAUSAL DISTANCE",
# # # #             "value": (
# # # #                 f"{float(cce.d_causal):.4f}"
# # # #             ),
# # # #             "explanation": (
# # # #                 "How far the proposed state is\n"
# # # #                 "from the observed causal state."
# # # #             ),
# # # #         },

# # # #         {
# # # #             "title": "RUNTIME",
# # # #             "value": (
# # # #                 f"{float(cce.runtime):.2f} s"
# # # #             ),
# # # #             "explanation": (
# # # #                 "Time required to compute\n"
# # # #                 "the explanation."
# # # #             ),
# # # #         },
# # # #     ]

# # # #     _show_metric_cards(
# # # #         metrics
# # # #     )

# # # #     # ============================================================
# # # #     # 4. COUNTERFACTUAL ACTION
# # # #     # ============================================================

# # # #     print(
# # # #         "\n4. WHAT WOULD NEED TO CHANGE?"
# # # #     )

# # # #     _line()

# # # #     if direct:

# # # #         rows = []

# # # #         for j in direct:

# # # #             old = float(
# # # #                 cce.x_obs[j]
# # # #             )

# # # #             new = float(
# # # #                 cce.x_star[j]
# # # #             )

# # # #             delta = new - old

# # # #             rows.append(
# # # #                 [
# # # #                     "★",
# # # #                     names[j],
# # # #                     f"{old:.4f}",
# # # #                     f"{new:.4f}",
# # # #                     f"{delta:+.4f}",
# # # #                     _format_change(
# # # #                         old,
# # # #                         new,
# # # #                     ),
# # # #                 ]
# # # #             )

# # # #         _show_table(
# # # #             rows,
# # # #             [
# # # #                 "",
# # # #                 "Feature",
# # # #                 "Current",
# # # #                 "Required",
# # # #                 "Δ",
# # # #                 "Action",
# # # #             ],
# # # #             title="Direct causal actions",
# # # #         )

# # # #     else:

# # # #         print(
# # # #             "  No direct causal intervention "
# # # #             "was identified."
# # # #         )

# # # #     # ============================================================
# # # #     # 5. DOWNSTREAM SUMMARY
# # # #     # ============================================================

# # # #     print("\n5. CAUSAL PROPAGATION")
# # # #     _line()

# # # #     if downstream:

# # # #         print(
# # # #             f"  The direct intervention propagates "
# # # #             f"through {downstream_count} downstream feature(s)."
# # # #         )

# # # #         print(
# # # #             "  These are consequences of the causal "
# # # #             "structure, not additional user actions."
# # # #         )

# # # #         # Only show a compact table.

# # # #         rows = []

# # # #         for j in downstream:

# # # #             old = float(
# # # #                 cce.x_obs[j]
# # # #             )

# # # #             new = float(
# # # #                 cce.x_star[j]
# # # #             )

# # # #             rows.append(
# # # #                 [
# # # #                     names[j],
# # # #                     f"{old:.4f}",
# # # #                     f"{new:.4f}",
# # # #                     f"{new - old:+.4f}",
# # # #                 ]
# # # #             )

# # # #         _show_table(
# # # #             rows,
# # # #             [
# # # #                 "Feature",
# # # #                 "Original",
# # # #                 "After propagation",
# # # #                 "Change",
# # # #             ],
# # # #             title="Downstream causal effects",
# # # #             figsize=(
# # # #                 10,
# # # #                 max(
# # # #                     3,
# # # #                     min(
# # # #                         12,
# # # #                         1.5 + 0.35 * len(rows),
# # # #                     ),
# # # #                 ),
# # # #             ),
# # # #         )

# # # #     else:

# # # #         print(
# # # #             "  No downstream causal changes."
# # # #         )

# # # #     # ============================================================
# # # #     # 6. TOP CAUSAL FACTORS
# # # #     # ============================================================

# # # #     print("\n6. TOP CAUSAL FACTORS")
# # # #     _line()

# # # #     top_k = min(
# # # #         5,
# # # #         len(order),
# # # #     )

# # # #     rows = []

# # # #     for rank in range(top_k):

# # # #         j = int(
# # # #             order[rank]
# # # #         )

# # # #         effect = float(
# # # #             cai_values[j]
# # # #         )

# # # #         rows.append(
# # # #             [
# # # #                 rank + 1,
# # # #                 names[j],
# # # #                 f"{effect:+.4f}",
# # # #                 _effect_description(
# # # #                     effect
# # # #                 ),
# # # #             ]
# # # #         )

# # # #     _show_table(
# # # #         rows,
# # # #         [
# # # #             "Rank",
# # # #             "Feature",
# # # #             "CAI",
# # # #             "Interpretation",
# # # #         ],
# # # #         title="Top causal factors",
# # # #         figsize=(
# # # #             10,
# # # #             4,
# # # #         ),
# # # #     )

# # # #     # ============================================================
# # # #     # 7. FINAL CONCLUSION
# # # #     # ============================================================

# # # #     print("\n7. CONCLUSION")
# # # #     _line()

# # # #     print(
# # # #         f"  {_direction_sentence(names[top], top_effect)}"
# # # #     )

# # # #     if cce.feasible:

# # # #         print(
# # # #             f"\n  A causal intervention changes the "
# # # #             f"model output from "
# # # #             f"{cce.y_fact:.4f} to "
# # # #             f"{cce.y_achieved:.4f}."
# # # #         )

# # # #     else:

# # # #         print(
# # # #             f"\n  The requested target "
# # # #             f"{cce.y_foil:.4f} could not be reached "
# # # #             "under the learned causal constraints."
# # # #         )

# # # #     print()


# # # # # ================================================================
# # # # # 4. CAI VS SHAP
# # # # # ================================================================

# # # # def show_cai_vs_shap(
# # # #     comparison: dict,
# # # #     feature_names=None,
# # # # ):
# # # #     """
# # # #     Display CAI vs observational SHAP-style attribution.

# # # #     Shows:

# # # #         1. Interpretation summary
# # # #         2. CAI vs SHAP scatter plot
# # # #         3. Difference plot
# # # #         4. Existing detailed comparison table
# # # #     """

# # # #     if not isinstance(
# # # #         comparison,
# # # #         dict,
# # # #     ):
# # # #         raise TypeError(
# # # #             "comparison must be a dictionary."
# # # #         )

# # # #     required = {
# # # #         "cai",
# # # #         "shap_style",
# # # #         "baseline_int",
# # # #         "baseline_obs",
# # # #     }

# # # #     missing = [
# # # #         key
# # # #         for key in required
# # # #         if key not in comparison
# # # #     ]

# # # #     if missing:

# # # #         raise KeyError(
# # # #             "CAI vs SHAP comparison is missing: "
# # # #             + ", ".join(missing)
# # # #         )

# # # #     cai = np.asarray(
# # # #         comparison["cai"],
# # # #         dtype=float,
# # # #     )

# # # #     shap = np.asarray(
# # # #         comparison["shap_style"],
# # # #         dtype=float,
# # # #     )

# # # #     if cai.shape != shap.shape:

# # # #         raise ValueError(
# # # #             "CAI and SHAP arrays must have "
# # # #             "the same shape."
# # # #         )

# # # #     names = _names(
# # # #         cai,
# # # #         feature_names,
# # # #     )

# # # #     difference = (
# # # #         cai - shap
# # # #     )

# # # #     bias_threshold = 0.05

# # # #     order = np.argsort(
# # # #         np.abs(difference)
# # # #     )[::-1]

# # # #     _header(
# # # #         "CAUSAL vs OBSERVATIONAL ATTRIBUTION"
# # # #     )

# # # #     # ============================================================
# # # #     # Interpretation
# # # #     # ============================================================

# # # #     print(
# # # #         "\nCAI"
# # # #     )

# # # #     _line()

# # # #     print(
# # # #         "  Measures the change in expected model output "
# # # #         "under an active feature intervention."
# # # #     )

# # # #     print(
# # # #         "\nSHAP-style"
# # # #     )

# # # #     _line()

# # # #     print(
# # # #         "  Describes feature contribution using "
# # # #         "observational relationships."
# # # #     )

# # # #     print(
# # # #         "\nWhy compare them?"
# # # #     )

# # # #     _line()

# # # #     print(
# # # #         "  Large disagreement means that the feature's "
# # # #         "observational contribution differs from its "
# # # #         "estimated interventional causal effect."
# # # #     )

# # # #     # ============================================================
# # # #     # Baselines
# # # #     # ============================================================

# # # #     print(
# # # #         "\nREFERENCE OUTPUTS"
# # # #     )

# # # #     _line()

# # # #     print(
# # # #         f"  Interventional baseline : "
# # # #         f"{comparison['baseline_int']:.4f}"
# # # #     )

# # # #     print(
# # # #         f"  Observational baseline  : "
# # # #         f"{comparison['baseline_obs']:.4f}"
# # # #     )

# # # #     # ============================================================
# # # #     # Scatter plot
# # # #     # ============================================================

# # # #     plt = _get_plt()

# # # #     fig, ax = plt.subplots(
# # # #         figsize=(7, 4.2)
# # # #     )

# # # #     ax.scatter(
# # # #         shap,
# # # #         cai,
# # # #         s=42,
# # # #     )

# # # #     minimum = min(
# # # #         float(np.min(shap)),
# # # #         float(np.min(cai)),
# # # #     )

# # # #     maximum = max(
# # # #         float(np.max(shap)),
# # # #         float(np.max(cai)),
# # # #     )

# # # #     padding = (
# # # #         maximum - minimum
# # # #     ) * 0.08 + 1e-6

# # # #     ax.plot(
# # # #         [
# # # #             minimum - padding,
# # # #             maximum + padding,
# # # #         ],
# # # #         [
# # # #             minimum - padding,
# # # #             maximum + padding,
# # # #         ],
# # # #         linestyle="--",
# # # #         linewidth=1.5,
# # # #     )

# # # #     for i in range(
# # # #         len(names)
# # # #     ):

# # # #         ax.annotate(
# # # #             names[i],
# # # #             (
# # # #                 shap[i],
# # # #                 cai[i],
# # # #             ),
# # # #             fontsize=7,
# # # #             xytext=(4, 4),
# # # #             textcoords="offset points",
# # # #         )

# # # #     ax.set_xlabel(
# # # #         "SHAP-style attribution"
# # # #     )

# # # #     ax.set_ylabel(
# # # #         "CAI"
# # # #     )

# # # #     ax.set_title(
# # # #         "CAI vs SHAP-style attribution",
# # # #         fontweight="bold",
# # # #     )

# # # #     ax.grid(
# # # #         alpha=0.2
# # # #     )

# # # #     plt.tight_layout()
# # # #     plt.show()

# # # #     # ============================================================
# # # #     # Difference chart
# # # #     # ============================================================

# # # #     sorted_names = [
# # # #         names[int(j)]
# # # #         for j in order
# # # #     ]

# # # #     sorted_difference = [
# # # #         float(difference[int(j)])
# # # #         for j in order
# # # #     ]

# # # #     fig, ax = plt.subplots(
# # # #         figsize=(
# # # #             10,
# # # #             max(
# # # #                 5,
# # # #                 0.35 * len(order),
# # # #             ),
# # # #         )
# # # #     )

# # # #     y = np.arange(
# # # #         len(order)
# # # #     )

# # # #     ax.barh(
# # # #         y,
# # # #         sorted_difference,
# # # #     )

# # # #     ax.axvline(
# # # #         0,
# # # #         linewidth=1,
# # # #     )

# # # #     ax.set_yticks(
# # # #         y
# # # #     )

# # # #     ax.set_yticklabels(
# # # #         sorted_names
# # # #     )

# # # #     ax.invert_yaxis()

# # # #     ax.set_xlabel(
# # # #         "CAI − SHAP-style"
# # # #     )

# # # #     ax.set_title(
# # # #         "Where CAI and SHAP-style attribution disagree",
# # # #         fontweight="bold",
# # # #     )

# # # #     plt.tight_layout()
# # # #     plt.show()

# # # #     # ============================================================
# # # #     # Existing detailed table
# # # #     # ============================================================

# # # #     print(
# # # #         "\nDETAILED COMPARISON"
# # # #     )

# # # #     _line()

# # # #     rows = []

# # # #     n_biased = 0

# # # #     for rank, j in enumerate(order):

# # # #         j = int(j)

# # # #         diff = float(
# # # #             difference[j]
# # # #         )

# # # #         biased = (
# # # #             abs(diff)
# # # #             > bias_threshold
# # # #         )

# # # #         if biased:
# # # #             n_biased += 1

# # # #         rows.append(
# # # #             [
# # # #                 rank + 1,
# # # #                 names[j],
# # # #                 f"{cai[j]:+.4f}",
# # # #                 f"{shap[j]:+.4f}",
# # # #                 f"{diff:+.4f}",
# # # #                 "⚠" if biased else "✓",
# # # #             ]
# # # #         )

# # # #     _show_table(
# # # #         rows,
# # # #         [
# # # #             "Rank",
# # # #             "Feature",
# # # #             "CAI",
# # # #             "SHAP",
# # # #             "Difference",
# # # #             "Flag",
# # # #         ],
# # # #         title="CAI vs SHAP-style comparison",
# # # #         figsize=(
# # # #             11,
# # # #             max(
# # # #                 4,
# # # #                 min(
# # # #                     15,
# # # #                     1.5 + 0.35 * len(rows),
# # # #                 ),
# # # #             ),
# # # #         ),
# # # #         font_size=8,
# # # #     )

# # # #     print(
# # # #         f"\n  Features with |CAI − SHAP| > "
# # # #         f"{bias_threshold:.2f}: "
# # # #         f"{n_biased}/{len(cai)}"
# # # #     )

# # # #     if len(order):

# # # #         largest = int(
# # # #             order[0]
# # # #         )

# # # #         print(
# # # #             "\nLARGEST DISAGREEMENT"
# # # #         )

# # # #         _line()

# # # #         print(
# # # #             f"  Feature    : "
# # # #             f"{names[largest]}"
# # # #         )

# # # #         print(
# # # #             f"  CAI        : "
# # # #             f"{cai[largest]:+.4f}"
# # # #         )

# # # #         print(
# # # #             f"  SHAP       : "
# # # #             f"{shap[largest]:+.4f}"
# # # #         )

# # # #         print(
# # # #             f"  Difference : "
# # # #             f"{difference[largest]:+.4f}"
# # # #         )

# # # #     print()


# # # # # ================================================================
# # # # # 5. FIT DISPLAY
# # # # # ================================================================

# # # # def show_fit(
# # # #     model,
# # # #     feature_names=None,
# # # #     verbose=False,
# # # # ):
# # # #     """
# # # #     Display the fitted CAUSE-XAI model.

# # # #     Shows:

# # # #         - model readiness
# # # #         - causal graph
# # # #         - causal structure summary
# # # #         - optional ANM mechanism details
# # # #     """

# # # #     _header(
# # # #         "CAUSE-XAI — MODEL READY"
# # # #     )

# # # #     print(
# # # #         "\nMODEL STATUS"
# # # #     )

# # # #     _line()

# # # #     print(
# # # #         "  ✓ Causal structure discovered"
# # # #     )

# # # #     print(
# # # #         "  ✓ Causal mechanisms fitted"
# # # #     )

# # # #     print(
# # # #         "  ✓ Model ready for explanation"
# # # #     )

# # # #     # ============================================================
# # # #     # Adjacency
# # # #     # ============================================================

# # # #     adj = getattr(
# # # #         model,
# # # #         "_adj",
# # # #         None,
# # # #     )

# # # #     if adj is None:

# # # #         adj = getattr(
# # # #             model,
# # # #             "adj_",
# # # #             None,
# # # #         )

# # # #     if adj is None:

# # # #         print(
# # # #             "\n  Causal structure information "
# # # #             "is unavailable."
# # # #         )

# # # #         return

# # # #     adj = np.asarray(
# # # #         adj
# # # #     )

# # # #     p = adj.shape[0]

# # # #     names = (
# # # #         list(feature_names)
# # # #         if feature_names is not None
# # # #         else [
# # # #             f"X{i + 1}"
# # # #             for i in range(p)
# # # #         ]
# # # #     )

# # # #     edges = []

# # # #     for i in range(p):

# # # #         for j in range(p):

# # # #             if adj[i, j] != 0:

# # # #                 edges.append(
# # # #                     (
# # # #                         i,
# # # #                         j,
# # # #                     )
# # # #                 )

# # # #     parents = {
# # # #         j: []
# # # #         for j in range(p)
# # # #     }

# # # #     children = {
# # # #         i: []
# # # #         for i in range(p)
# # # #     }

# # # #     for i, j in edges:

# # # #         children[i].append(j)
# # # #         parents[j].append(i)

# # # #     roots = [
# # # #         names[i]
# # # #         for i in range(p)
# # # #         if not parents[i]
# # # #     ]

# # # #     sinks = [
# # # #         names[i]
# # # #         for i in range(p)
# # # #         if not children[i]
# # # #     ]

# # # #     print(
# # # #         "\nCAUSAL STRUCTURE"
# # # #     )

# # # #     _line()

# # # #     rows = [

# # # #         [
# # # #             "Variables",
# # # #             p,
# # # #         ],

# # # #         [
# # # #             "Relationships discovered",
# # # #             len(edges),
# # # #         ],

# # # #         [
# # # #             "Root variables",
# # # #             len(roots),
# # # #         ],

# # # #         [
# # # #             "Sink variables",
# # # #             len(sinks),
# # # #         ],

# # # #     ]

# # # #     _show_table(
# # # #         rows,
# # # #         [
# # # #             "Property",
# # # #             "Value",
# # # #         ],
# # # #         title="Learned causal structure",
# # # #         figsize=(
# # # #             7,
# # # #             3.5,
# # # #         ),
# # # #     )

# # # #     # ============================================================
# # # #     # DAG
# # # #     # ============================================================

# # # #     try:

# # # #         dag = show_dag(
# # # #             model,
# # # #             feature_names=names,
# # # #         )

# # # #         if dag is not None:

# # # #             try:

# # # #                 dag.view()

# # # #             except Exception:

# # # #                 print(
# # # #                     "\n  DAG object created successfully."
# # # #                 )

# # # #     except Exception as exc:

# # # #         print(
# # # #             f"\n  DAG visualization unavailable: "
# # # #             f"{exc}"
# # # #         )

# # # #     # ============================================================
# # # #     # ANM details
# # # #     # ============================================================

# # # #     if verbose:

# # # #         anm = getattr(
# # # #             model,
# # # #             "anm_",
# # # #             None,
# # # #         )

# # # #         if anm is not None:

# # # #             print(
# # # #                 "\nCAUSAL MECHANISM FIT"
# # # #             )

# # # #             _line()

# # # #             rows = []

# # # #             residual_std = getattr(
# # # #                 anm,
# # # #                 "residual_std",
# # # #                 {},
# # # #             )

# # # #             noise = getattr(
# # # #                 anm,
# # # #                 "noise",
# # # #                 {},
# # # #             )

# # # #             eqs = getattr(
# # # #                 anm,
# # # #                 "eqs",
# # # #                 {},
# # # #             )

# # # #             for j in anm.order:

# # # #                 variable = (
# # # #                     names[j]
# # # #                     if j < len(names)
# # # #                     else f"X{j + 1}"
# # # #                 )

# # # #                 eq = eqs.get(
# # # #                     j
# # # #                 )

# # # #                 parent_names = []

# # # #                 if eq is not None:

# # # #                     for parent in eq.parents:

# # # #                         if parent < len(names):

# # # #                             parent_names.append(
# # # #                                 names[parent]
# # # #                             )

# # # #                         else:

# # # #                             parent_names.append(
# # # #                                 f"X{parent + 1}"
# # # #                             )

# # # #                 parents_text = (
# # # #                     ", ".join(parent_names)
# # # #                     if parent_names
# # # #                     else "None"
# # # #                 )

# # # #                 noise_text = "-"

# # # #                 if j in noise:

# # # #                     loc, scale = noise[j]

# # # #                     noise_text = (
# # # #                         f"Laplace("
# # # #                         f"loc={loc:.3f}, "
# # # #                         f"scale={scale:.3f})"
# # # #                     )

# # # #                 std = residual_std.get(
# # # #                     j,
# # # #                     np.nan,
# # # #                 )

# # # #                 rows.append(
# # # #                     [
# # # #                         variable,
# # # #                         parents_text,
# # # #                         noise_text,
# # # #                         f"{float(std):.4f}",
# # # #                     ]
# # # #                 )

# # # #             _show_table(
# # # #                 rows,
# # # #                 [
# # # #                     "Variable",
# # # #                     "Parents",
# # # #                     "Noise",
# # # #                     "Residual std",
# # # #                 ],
# # # #                 title="Fitted causal mechanisms",
# # # #                 figsize=(
# # # #                     12,
# # # #                     max(
# # # #                         4,
# # # #                         min(
# # # #                             15,
# # # #                             1.5 + 0.35 * len(rows),
# # # #                         ),
# # # #                     ),
# # # #                 ),
# # # #                 font_size=8,
# # # #             )

# # # #     print()


# # # # # ================================================================
# # # # # DAG DISPLAY
# # # # # ================================================================

# # # # def show_dag(
# # # #     model,
# # # #     feature_names=None,
# # # # ):
# # # #     """
# # # #     Create a Graphviz representation of the learned DAG.

# # # #     Returns
# # # #     -------
# # # #     graphviz.Digraph or None
# # # #     """

# # # #     try:

# # # #         from graphviz import Digraph

# # # #     except ImportError:

# # # #         print(
# # # #             "DAG visualization requires the Python "
# # # #             "graphviz package."
# # # #         )

# # # #         print(
# # # #             "Install with:"
# # # #         )

# # # #         print(
# # # #             "    pip install graphviz"
# # # #         )

# # # #         return None

# # # #     adj = np.asarray(
# # # #         model._adj
# # # #     )

# # # #     p = adj.shape[0]

# # # #     if feature_names is not None:

# # # #         names = list(
# # # #             feature_names
# # # #         )

# # # #     else:

# # # #         names = [
# # # #             f"X{i + 1}"
# # # #             for i in range(p)
# # # #         ]

# # # #     dot = Digraph(
# # # #         "CAUSE_XAI_DAG"
# # # #     )

# # # #     dot.attr(
# # # #         rankdir="LR",
# # # #         splines="ortho",
# # # #         nodesep="0.30",
# # # #         ranksep="0.55",
# # # #         bgcolor="white",
# # # #     )

# # # #     dot.attr(
# # # #         "node",
# # # #         shape="box",
# # # #         style="rounded",
# # # #         fontsize="9",
# # # #         margin="0.08",
# # # #     )

# # # #     dot.attr(
# # # #         "edge",
# # # #         arrowsize="0.55",
# # # #         penwidth="0.9",
# # # #     )

# # # #     for i, name in enumerate(names):

# # # #         has_parent = np.any(
# # # #             adj[:, i]
# # # #         )

# # # #         has_child = np.any(
# # # #             adj[i, :]
# # # #         )

# # # #         if not has_parent:

# # # #             label = (
# # # #                 f"{name}\\n(root)"
# # # #             )

# # # #         elif not has_child:

# # # #             label = (
# # # #                 f"{name}\\n(sink)"
# # # #             )

# # # #         else:

# # # #             label = name

# # # #         dot.node(
# # # #             str(i),
# # # #             label,
# # # #         )

# # # #     for i in range(p):

# # # #         for j in range(p):

# # # #             if adj[i, j] != 0:

# # # #                 dot.edge(
# # # #                     str(i),
# # # #                     str(j),
# # # #                 )

# # # #     return dot


# # # # # ================================================================
# # # # # GENERIC DISPLAY
# # # # # ================================================================

# # # # def display(
# # # #     result,
# # # #     feature_names=None,
# # # # ):
# # # #     """
# # # #     Automatically select the appropriate CAUSE-XAI display.

# # # #     No task/classification/regression argument is required.
# # # #     """

# # # #     if isinstance(
# # # #         result,
# # # #         UnifiedExplanation,
# # # #     ):

# # # #         return show_explanation(
# # # #             result,
# # # #             feature_names=feature_names,
# # # #         )

# # # #     if isinstance(
# # # #         result,
# # # #         CCEResult,
# # # #     ):

# # # #         return show_counterfactual(
# # # #             result,
# # # #             feature_names=feature_names,
# # # #         )

# # # #     if isinstance(
# # # #         result,
# # # #         CAIResult,
# # # #     ):

# # # #         return show_attribution(
# # # #             result,
# # # #             feature_names=feature_names,
# # # #         )

# # # #     if isinstance(
# # # #         result,
# # # #         dict,
# # # #     ):

# # # #         if (
# # # #             "cai" in result
# # # #             and "shap_style" in result
# # # #         ):

# # # #             return show_cai_vs_shap(
# # # #                 result,
# # # #                 feature_names=feature_names,
# # # #             )

# # # #         raise TypeError(
# # # #             "Dictionary does not contain a recognised "
# # # #             "CAUSE-XAI result."
# # # #         )

# # # #     raise TypeError(
# # # #         f"Unsupported result type: "
# # # #         f"{type(result).__name__}"
# # # #     )


# # # # # ================================================================
# # # # # PUBLIC API
# # # # # ================================================================

# # # # __all__ = [
# # # #     "show_fit",
# # # #     "show_counterfactual",
# # # #     "show_attribution",
# # # #     "show_explanation",
# # # #     "show_cai_vs_shap",
# # # #     "show_dag",
# # # #     "display",

# # # # ]

# # # # src/cause/display.py

# # # """
# # # User-facing display layer for CAUSE-XAI.

# # # Principles:
# # # - No internal details (no do(...), no edges, no DAG tables).
# # # - No plots by default.
# # # - No "model output" horizontal graph in counterfactual.
# # # - Minimal spacing, no excessive lines.
# # # - Simple, SHAP/LIME-style wording.
# # # - User flow:
# # #     fit()          → one clean summary
# # #     counterfactual() → clean counterfactual
# # #     explain()      → unified explanation (uses CAI internally, no separate CAI.summary())
# # # """

# # # import numpy as np

# # # from .results import CCEResult, CAIResult, UnifiedExplanation


# # # # ================================================================
# # # # HELPERS
# # # # ================================================================


# # # def _names(values, feature_names=None):
# # #     """Return readable feature names."""
# # #     n = len(values)
# # #     if feature_names is not None:
# # #         if len(feature_names) != n:
# # #             raise ValueError(
# # #                 "feature_names must have the same length as the number of features."
# # #             )
# # #         return list(feature_names)
# # #     return [f"Feature {i + 1}" for i in range(n)]


# # # def _line(char="─", width=72):
# # #     print(char * width)


# # # def _header(title, width=72):
# # #     print()
# # #     print("═" * width)
# # #     print(title.center(width))
# # #     print("═" * width)


# # # def _format_change(old, new):
# # #     """Convert a numerical change into readable language."""
# # #     delta = float(new) - float(old)
# # #     if abs(delta) < 1e-10:
# # #         return "no change"
# # #     if delta > 0:
# # #         return f"increase by {abs(delta):.3f}"
# # #     return f"decrease by {abs(delta):.3f}"


# # # def _effect_description(effect):
# # #     """Human-readable CAI interpretation (generic)."""
# # #     effect = float(effect)
# # #     if abs(effect) < 1e-10:
# # #         return "Little measurable influence"
# # #     magnitude = abs(effect)
# # #     if effect > 0:
# # #         if magnitude >= 0.20:
# # #             return "Strong increase"
# # #         if magnitude >= 0.10:
# # #             return "Moderate increase"
# # #         return "Small increase"
# # #     if magnitude >= 0.20:
# # #         return "Strong decrease"
# # #     if magnitude >= 0.10:
# # #         return "Moderate decrease"
# # #     return "Small decrease"


# # # def _direction_sentence(feature, effect):
# # #     """Natural-language causal direction."""
# # #     effect = float(effect)
# # #     if effect > 0:
# # #         return (
# # #             f"{feature} has the strongest estimated causal influence "
# # #             f"and increases the expected model output."
# # #         )
# # #     if effect < 0:
# # #         return (
# # #             f"{feature} has the strongest estimated causal influence "
# # #             f"and decreases the expected model output."
# # #         )
# # #     return (
# # #         f"{feature} has little measurable causal influence "
# # #         f"on the expected model output."
# # #     )


# # # # ================================================================
# # # # 1. FIT DISPLAY
# # # # ================================================================


# # # def show_fit(model, feature_names=None, verbose=False):
# # #     """
# # #     Display the fitted CAUSE-XAI model.

# # #     Shows:
# # #       - model readiness
# # #       - causal structure summary
# # #     No internal DAG tables, no ANM mechanism details by default.
# # #     """
# # #     _header("CAUSE-XAI — MODEL READY")

# # #     print("\nStatus")
# # #     _line()
# # #     print("  ✓ Causal structure discovered")
# # #     print("  ✓ Causal mechanisms fitted")
# # #     print("  ✓ Model ready for explanation")

# # #     adj = getattr(model, "_adj", None)
# # #     if adj is None:
# # #         adj = getattr(model, "adj_", None)

# # #     if adj is None:
# # #         print("\nCausal structure information is unavailable.")
# # #         return

# # #     adj = np.asarray(adj)
# # #     p = adj.shape[0]

# # #     names = (
# # #         list(feature_names)
# # #         if feature_names is not None
# # #         else [f"X{i + 1}" for i in range(p)]
# # #     )

# # #     edges = []
# # #     for i in range(p):
# # #         for j in range(p):
# # #             if adj[i, j] != 0:
# # #                 edges.append((i, j))

# # #     parents = {j: [] for j in range(p)}
# # #     children = {i: [] for i in range(p)}

# # #     for i, j in edges:
# # #         children[i].append(j)
# # #         parents[j].append(i)

# # #     roots = [names[i] for i in range(p) if not parents[i]]
# # #     sinks = [names[i] for i in range(p) if not children[i]]

# # #     print("\nCausal structure")
# # #     _line()
# # #     print(f"  Variables                : {p}")
# # #     print(f"  Relationships discovered : {len(edges)}")
# # #     print(f"  Root variables           : {len(roots)}")
# # #     print(f"  Sink variables           : {len(sinks)}")

# # #     if verbose:
# # #         # Optional: show a few strongest relationships if you store scores
# # #         pass

# # #     print()


# # # # ================================================================
# # # # 2. COUNTERFACTUAL
# # # # ================================================================


# # # def show_counterfactual(result: CCEResult, feature_names=None):
# # #     """
# # #     Display a concise causal counterfactual explanation.

# # #     Shows:
# # #       - What would need to change (direct interventions only)
# # #       - Causal validity
# # #     No plots, no internal do(...) logs, no model-output graph.
# # #     """
# # #     names = _names(result.x_obs, feature_names)

# # #     _header("COUNTERFACTUAL EXPLANATION")

# # #     print("\nWhat would need to change?")
# # #     _line()

# # #     direct = result.direct_interventions or []

# # #     if result.feasible and direct:
# # #         for j in direct:
# # #             old = float(result.x_obs[j])
# # #             new = float(result.x_star[j])
# # #             print(f"\n  {names[j]}")
# # #             print(f"    Current value : {old:.3f}")
# # #             print(f"    New value     : {new:.3f}")
# # #             print(f"    Required      : {_format_change(old, new)}")
# # #     elif result.feasible and result.changed:
# # #         # Fallback if direct_interventions is missing
# # #         for j in result.changed:
# # #             old = float(result.x_obs[j])
# # #             new = float(result.x_star[j])
# # #             print(f"\n  {names[j]}")
# # #             print(f"    Current value : {old:.3f}")
# # #             print(f"    New value     : {new:.3f}")
# # #             print(f"    Required      : {_format_change(old, new)}")
# # #     else:
# # #         print(
# # #             "  No feasible feature change was found "
# # #             "under the current causal constraints."
# # #         )

# # #     print("\nCausal validity")
# # #     _line()
# # #     if result.violation < 1.5:
# # #         print(
# # #             "  ✓ The resulting state is consistent with "
# # #             "the learned causal structure."
# # #         )
# # #     else:
# # #         print(
# # #             "  ⚠ The resulting state may be inconsistent "
# # #             "with the learned causal structure."
# # #         )

# # #     print(f"\n  Causal distance : {result.d_causal:.3f}")
# # #     print(f"  Causal sparsity : {result.sparsity:.2f}")
# # #     print(f"  Runtime         : {result.runtime:.3f} sec")
# # #     print()


# # # # ================================================================
# # # # 3. CAUSAL FEATURE IMPACT (CAI) – INTERNAL USE
# # # # ================================================================


# # # def show_attribution(result: CAIResult, feature_names=None):
# # #     """
# # #     Display CAI attribution.

# # #     This is primarily used inside explain().
# # #     Users typically do not call this directly.
# # #     """
# # #     names = _names(result.x_obs, feature_names)
# # #     cai = np.asarray(result.cai, dtype=float)

# # #     if cai.size == 0:
# # #         _header("CAUSAL FEATURE IMPACT")
# # #         print("\n  No CAI values available.")
# # #         return

# # #     order = np.argsort(np.abs(cai))[::-1]
# # #     top = int(order[0])
# # #     top_effect = float(cai[top])

# # #     _header("CAUSAL FEATURE IMPACT")

# # #     print(
# # #         "\nThe causal effect estimates how intervening on each feature "
# # #         "changes the expected model output."
# # #     )

# # #     if result.n_samples is not None:
# # #         print(f"\n  Monte Carlo samples : {result.n_samples}")

# # #     print("\nFeature-level causal effects")
# # #     _line()

# # #     rows = []
# # #     for rank, j in enumerate(order):
# # #         j = int(j)
# # #         effect = float(cai[j])
# # #         rows.append(
# # #             [
# # #                 rank + 1,
# # #                 names[j],
# # #                 f"{effect:+.4f}",
# # #                 _effect_description(effect),
# # #             ]
# # #         )

# # #     # Simple text table, no matplotlib
# # #     print(f"{'Rank':<6}{'Feature':<20}{'CAI':>12}{'Interpretation':>25}")
# # #     _line(width=6 + 20 + 12 + 25)
# # #     for r in rows:
# # #         print(f"{r[0]:<6}{r[1]:<20}{r[2]:>12}{r[3]:>25}")

# # #     print("\nMain causal driver")
# # #     _line()
# # #     print(f"  {_direction_sentence(names[top], top_effect)}")
# # #     print(f"  CAI : {top_effect:+.4f}")
# # #     print(f"  Baseline expected output : {result.baseline:.4f}")
# # #     print()


# # # # ================================================================
# # # # 4. UNIFIED EXPLANATION
# # # # ================================================================


# # # def show_explanation(explanation: UnifiedExplanation, feature_names=None):
# # #     """
# # #     Main CAUSE-XAI explanation.

# # #     Shows:
# # #       1. Prediction
# # #       2. Top causal factors (from CAI, compact)
# # #       3. Counterfactual actions (direct interventions)
# # #       4. Causal validity
# # #       5. Plain-language conclusion

# # #     Does NOT show:
# # #       - Full CAI table
# # #       - Full downstream table
# # #       - Internal do(...) details
# # #     """
# # #     names = _names(explanation.x_obs, feature_names)

# # #     cce = explanation.cce
# # #     cai = explanation.cai

# # #     cai_values = np.asarray(cai.cai, dtype=float)

# # #     if cai_values.size == 0:
# # #         _header("CAUSE-XAI — MODEL EXPLANATION")
# # #         print("\n  No causal attribution values available.")
# # #         return

# # #     order = np.argsort(np.abs(cai_values))[::-1]

# # #     _header("CAUSE-XAI — MODEL EXPLANATION")

# # #     # 1. Prediction
# # #     print("\n1. Prediction")
# # #     _line()
# # #     print(f"  Current output : {explanation.y_fact:.4f}")
# # #     print(f"  Target output  : {explanation.y_foil:.4f}")
# # #     print(f"  Achieved output: {cce.y_achieved:.4f}")

# # #     if cce.feasible:
# # #         print("\n  ✓ A feasible causal counterfactual was found.")
# # #     else:
# # #         print("\n  ✗ The requested target could not be reached.")

# # #     # 2. Top causal factors (compact)
# # #     print("\n2. Top causal factors")
# # #     _line()

# # #     top_k = min(3, len(order))
# # #     for rank in range(top_k):
# # #         j = int(order[rank])
# # #         effect = float(cai_values[j])
# # #         desc = _effect_description(effect)
# # #         print(f"  {rank + 1}. {names[j]:<18} {effect:>+10.4f}   {desc}")

# # #     # 3. Counterfactual actions (direct interventions)
# # #     print("\n3. What would need to change?")
# # #     _line()

# # #     direct = cce.direct_interventions or []

# # #     if cce.feasible and direct:
# # #         for j in direct:
# # #             old = float(cce.x_obs[j])
# # #             new = float(cce.x_star[j])
# # #             print(f"\n  {names[j]}")
# # #             print(f"    Current : {old:.4f}")
# # #             print(f"    Desired : {new:.4f}")
# # #             print(f"    Action  : {_format_change(old, new)}")
# # #     elif cce.feasible and cce.changed:
# # #         # Fallback
# # #         print("\n  The solution changes the following features:")
# # #         for j in cce.changed[:5]:
# # #             old = float(cce.x_obs[j])
# # #             new = float(cce.x_star[j])
# # #             print(f"    {names[j]}: {old:.4f} → {new:.4f}")
# # #     else:
# # #         print("\n  No feasible change was found that reaches the target.")

# # #     # 4. Causal validity
# # #     print("\n4. Causal validity")
# # #     _line()
# # #     if cce.violation < 1.5:
# # #         print(
# # #             "  ✓ The counterfactual remains consistent with "
# # #             "the learned causal structure."
# # #         )
# # #     else:
# # #         print(
# # #             "  ⚠ The counterfactual may violate the learned causal structure."
# # #         )

# # #     # 5. Plain-language summary
# # #     print("\n5. Summary")
# # #     _line()

# # #     top = int(order[0])
# # #     top_effect = float(cai_values[top])
# # #     print(f"  {_direction_sentence(names[top], top_effect)}")

# # #     if cce.feasible:
# # #         print(
# # #             f"\n  A causal intervention changes the model output from "
# # #             f"{cce.y_fact:.4f} to {cce.y_achieved:.4f}."
# # #         )
# # #     else:
# # #         print(
# # #             f"\n  The requested target {cce.y_foil:.4f} could not be reached "
# # #             "under the learned causal constraints."
# # #         )

# # #     print()


# # # # ================================================================
# # # # 5. CAI VS SHAP (TECHNICAL, OPTIONAL)
# # # # ================================================================


# # # def show_cai_vs_shap(comparison: dict, feature_names=None):
# # #     """
# # #     Technical comparison between CAI and SHAP-style attribution.

# # #     Shows:
# # #       - Interpretation summary
# # #       - Detailed comparison table
# # #     No plots by default.
# # #     """
# # #     if not isinstance(comparison, dict):
# # #         raise TypeError("comparison must be a dictionary.")

# # #     required = {"cai", "shap_style"}
# # #     missing = [key for key in required if key not in comparison]
# # #     if missing:
# # #         raise KeyError(
# # #             "CAI vs SHAP comparison is missing: " + ", ".join(missing)
# # #         )

# # #     cai = np.asarray(comparison["cai"], dtype=float)
# # #     shap = np.asarray(comparison["shap_style"], dtype=float)

# # #     if cai.shape != shap.shape:
# # #         raise ValueError("CAI and SHAP arrays must have the same shape.")

# # #     names = _names(cai, feature_names)
# # #     difference = cai - shap
# # #     order = np.argsort(np.abs(difference))[::-1]

# # #     _header("CAUSAL vs OBSERVATIONAL ATTRIBUTION")

# # #     print("\nCAI")
# # #     _line()
# # #     print(
# # #         "  Measures the change in expected model output under "
# # #         "an active feature intervention."
# # #     )

# # #     print("\nSHAP-style")
# # #     _line()
# # #     print(
# # #         "  Describes feature contribution using observational relationships."
# # #     )

# # #     print("\nWhy compare them?")
# # #     _line()
# # #     print(
# # #         "  Large disagreement means that the feature's observational "
# # #         "contribution differs from its estimated interventional effect."
# # #     )

# # #     print("\nDetailed comparison")
# # #     _line()

# # #     rows = []
# # #     for rank, j in enumerate(order):
# # #         j = int(j)
# # #         diff = float(difference[j])
# # #         rows.append(
# # #             [
# # #                 rank + 1,
# # #                 names[j],
# # #                 f"{cai[j]:+.4f}",
# # #                 f"{shap[j]:+.4f}",
# # #                 f"{diff:+.4f}",
# # #             ]
# # #         )

# # #     print(
# # #         f"{'Rank':<6}{'Feature':<20}{'CAI':>12}{'SHAP':>12}{'Difference':>14}"
# # #     )
# # #     _line(width=6 + 20 + 12 + 12 + 14)
# # #     for r in rows:
# # #         print(f"{r[0]:<6}{r[1]:<20}{r[2]:>12}{r[3]:>12}{r[4]:>14}")

# # #     print()


# # # # ================================================================
# # # # 6. GENERIC DISPATCH
# # # # ================================================================


# # # def display(result, feature_names=None):
# # #     """
# # #     Automatically select the appropriate CAUSE-XAI display.
# # #     """
# # #     if isinstance(result, UnifiedExplanation):
# # #         return show_explanation(result, feature_names=feature_names)
# # #     if isinstance(result, CCEResult):
# # #         return show_counterfactual(result, feature_names=feature_names)
# # #     if isinstance(result, CAIResult):
# # #         return show_attribution(result, feature_names=feature_names)
# # #     if isinstance(result, dict):
# # #         if "cai" in result and "shap_style" in result:
# # #             return show_cai_vs_shap(result, feature_names=feature_names)
# # #         raise TypeError(
# # #             "Dictionary does not contain a recognised CAUSE-XAI result."
# # #         )
# # #     raise TypeError(f"Unsupported result type: {type(result).__name__}")


# # # __all__ = [
# # #     "show_fit",
# # #     "show_counterfactual",
# # #     "show_attribution",
# # #     "show_explanation",
# # #     "show_cai_vs_shap",
# # #     "display",
# # # ]

# # import numpy as np

# # from .results import CCEResult, CAIResult, UnifiedExplanation


# # def _get_plt():
# #     try:
# #         import matplotlib.pyplot as plt
# #         return plt
# #     except ImportError as exc:
# #         raise ImportError(
# #             "CAUSE-XAI graphical displays require matplotlib.\n"
# #             "Install it with:\n"
# #             "    pip install matplotlib"
# #         ) from exc


# # def _names(values, feature_names=None):
# #     n = len(values)
# #     if feature_names is not None:
# #         if len(feature_names) != n:
# #             raise ValueError(
# #                 "feature_names must have the same length as the number of features."
# #             )
# #         return list(feature_names)
# #     return [f"Feature {i + 1}" for i in range(n)]


# # def _line(char="─", width=78):
# #     print(char * width)


# # def _header(title, width=78):
# #     print()
# #     print("═" * width)
# #     print(title.center(width))
# #     print("═" * width)


# # def _format_change(old, new):
# #     delta = float(new) - float(old)
# #     if abs(delta) < 1e-10:
# #         return "No change"
# #     if delta > 0:
# #         return f"Increase by {abs(delta):.3f}"
# #     return f"Decrease by {abs(delta):.3f}"


# # def _format_ci(ci):
# #     return f"[{float(ci[0]):+.4f}, {float(ci[1]):+.4f}]"


# # def _effect_description(effect):
# #     effect = float(effect)
# #     if abs(effect) < 1e-10:
# #         return "Little measurable influence"
# #     magnitude = abs(effect)
# #     if effect > 0:
# #         if magnitude >= 0.20:
# #             return "Strong increase"
# #         if magnitude >= 0.10:
# #             return "Moderate increase"
# #         return "Small increase"
# #     if magnitude >= 0.20:
# #         return "Strong decrease"
# #     if magnitude >= 0.10:
# #         return "Moderate decrease"
# #     return "Small decrease"


# # def _direction_sentence(feature, effect):
# #     effect = float(effect)
# #     if effect > 0:
# #         return (
# #             f"{feature} has the strongest estimated causal influence "
# #             f"and increases the expected model output."
# #         )
# #     if effect < 0:
# #         return (
# #             f"{feature} has the strongest estimated causal influence "
# #             f"and decreases the expected model output."
# #         )
# #     return (
# #         f"{feature} has little measurable causal influence "
# #         f"on the expected model output."
# #     )


# # def _show_table(rows, columns, title=None, figsize=None, font_size=9):
# #     plt = _get_plt()
# #     if figsize is None:
# #         figsize = (
# #             max(9, len(columns) * 1.5),
# #             max(2.5, min(14, 1.0 + 0.42 * len(rows))),
# #         )

# #     fig, ax = plt.subplots(figsize=figsize)
# #     ax.axis("off")
# #     if title is not None:
# #         ax.set_title(title, fontsize=13, pad=16, fontweight="bold")

# #     table = ax.table(
# #         cellText=rows,
# #         colLabels=columns,
# #         loc="center",
# #         cellLoc="center",
# #     )
# #     table.auto_set_font_size(False)
# #     table.set_fontsize(font_size)
# #     table.scale(1, 1.6)
# #     plt.tight_layout()
# #     plt.show()
# #     return fig


# # def _show_metric_cards(metrics):
# #     plt = _get_plt()
# #     n = len(metrics)
# #     cols = 3
# #     rows = int(np.ceil(n / cols))
# #     fig = plt.figure(figsize=(13, 3.0 * rows))

# #     for i, metric in enumerate(metrics):
# #         ax = fig.add_subplot(rows, cols, i + 1)
# #         ax.axis("off")
# #         ax.text(
# #             0.5, 0.76, metric["title"], ha="center", va="center",
# #             fontsize=10, fontweight="bold",
# #         )
# #         ax.text(
# #             0.5, 0.50, metric["value"], ha="center", va="center",
# #             fontsize=22, fontweight="bold",
# #         )
# #         ax.text(
# #             0.5, 0.19, metric["explanation"], ha="center", va="center",
# #             fontsize=8.5, wrap=True,
# #         )
# #         for spine in ax.spines.values():
# #             spine.set_visible(True)

# #     for i in range(n, rows * cols):
# #         ax = fig.add_subplot(rows, cols, i + 1)
# #         ax.axis("off")

# #     plt.tight_layout()
# #     plt.show()
# #     return fig


# # def _show_prediction_transition(current, achieved, target=None, title="Prediction change"):
# #     plt = _get_plt()
# #     current = float(current)
# #     achieved = float(achieved)
# #     fig, ax = plt.subplots(figsize=(11, 3.8))

# #     minimum = min(current, achieved)
# #     maximum = max(current, achieved)
# #     span = max(abs(maximum - minimum), 1e-6)
# #     ax.set_xlim(minimum - 0.15 * span, maximum + 0.15 * span)
# #     ax.set_ylim(-0.8, 0.8)
# #     ax.axhline(0, linewidth=2)
# #     ax.scatter([current], [0], s=120, zorder=5)
# #     ax.scatter([achieved], [0], s=120, zorder=5)
# #     ax.annotate(
# #         f"Current\n{current:.4f}", xy=(current, 0), xytext=(current, 0.45),
# #         ha="center", arrowprops=dict(arrowstyle="->"),
# #     )
# #     ax.annotate(
# #         f"After change\n{achieved:.4f}", xy=(achieved, 0),
# #         xytext=(achieved, -0.50), ha="center",
# #         arrowprops=dict(arrowstyle="->"),
# #     )
# #     ax.annotate(
# #         "", xy=(achieved, 0), xytext=(current, 0),
# #         arrowprops=dict(arrowstyle="<->", linewidth=2),
# #     )
# #     ax.text(
# #         (current + achieved) / 2, 0.13, f"Change: {achieved - current:+.4f}",
# #         ha="center", fontsize=10, fontweight="bold",
# #     )
# #     if target is not None:
# #         target = float(target)
# #         ax.axvline(target, linestyle="--", linewidth=1.5)
# #         ax.text(target, 0.68, f"Target\n{target:.4f}", ha="center", fontsize=8)
# #     ax.set_title(title, fontsize=13, fontweight="bold")
# #     ax.set_yticks([])
# #     ax.set_xlabel("Model output")
# #     plt.tight_layout()
# #     plt.show()
# #     return fig


# # def _value_at(values, index):
# #     if values is None:
# #         return None
# #     try:
# #         return float(values[index])
# #     except Exception:
# #         try:
# #             return float(np.asarray(values).reshape(-1)[index])
# #         except Exception:
# #             return None


# # # ================================================================
# # # 1. FIT DISPLAY
# # # ================================================================


# # def show_fit(model, feature_names=None, verbose=False):
# #     """Display model readiness, learned structure, and the learned DAG."""
# #     _header("CAUSE-XAI — MODEL READY")

# #     print("\nStatus")
# #     _line()
# #     print("  ✓ Causal structure discovered")
# #     print("  ✓ Causal mechanisms fitted")
# #     print("  ✓ Model ready for explanation")

# #     adj = getattr(model, "_adj", None)
# #     if adj is None:
# #         adj = getattr(model, "adj_", None)
# #     if adj is None:
# #         print("\nCausal structure information is unavailable.")
# #         return None

# #     adj = np.asarray(adj)
# #     p = adj.shape[0]
# #     names = list(feature_names) if feature_names is not None else [f"X{i + 1}" for i in range(p)]

# #     edges = [(i, j) for i in range(p) for j in range(p) if adj[i, j] != 0]
# #     parents = {j: [] for j in range(p)}
# #     children = {i: [] for i in range(p)}
# #     for i, j in edges:
# #         children[i].append(j)
# #         parents[j].append(i)

# #     roots = [names[i] for i in range(p) if not parents[i]]
# #     sinks = [names[i] for i in range(p) if not children[i]]

# #     print("\nCausal structure")
# #     _line()
# #     print(f"  Variables                : {p}")
# #     print(f"  Relationships discovered : {len(edges)}")
# #     print(f"  Root variables           : {len(roots)}")
# #     print(f"  Sink variables           : {len(sinks)}")

# #     if roots:
# #         print(f"  Roots                    : {', '.join(roots)}")

# #     print("\nDAG")
# #     _line()
# #     print("  Root variables are highlighted in the graph.")

# #     try:
# #         dag = show_dag(model, feature_names=names)
# #         if dag is not None:
# #             try:
# #                 dag.view()
# #             except Exception:
# #                 try:
# #                     from IPython.display import display as ipy_display
# #                     ipy_display(dag)
# #                 except Exception:
# #                     print("\n  DAG object created successfully.")
# #         return dag
# #     except Exception as exc:
# #         print(f"\n  DAG visualization unavailable: {exc}")
# #         return None


# # # ================================================================
# # # 2. COUNTERFACTUAL DISPLAY
# # # ================================================================


# # def show_counterfactual(result: CCEResult, feature_names=None):
# #     """Display the user-facing causal counterfactual and its causal diagnostics."""
# #     names = _names(result.x_obs, feature_names)
# #     _header("COUNTERFACTUAL EXPLANATION")

# #     print("\nWhat would need to change?")
# #     _line()
# #     direct = result.direct_interventions or []

# #     if result.feasible and direct:
# #         for j in direct:
# #             old = float(result.x_obs[j])
# #             new = float(result.x_star[j])
# #             print(f"\n  {names[j]}")
# #             print(f"    Current value : {old:.3f}")
# #             print(f"    New value     : {new:.3f}")
# #             print(f"    Required      : {_format_change(old, new).lower()}")
# #     elif result.feasible and result.changed:
# #         for j in result.changed:
# #             old = float(result.x_obs[j])
# #             new = float(result.x_star[j])
# #             print(f"\n  {names[j]}")
# #             print(f"    Current value : {old:.3f}")
# #             print(f"    New value     : {new:.3f}")
# #             print(f"    Required      : {_format_change(old, new).lower()}")
# #     else:
# #         print("  No feasible feature change was found under the current causal constraints.")

# #     print("\nCausal validity")
# #     _line()
# #     if float(result.violation) < 1.5:
# #         print("  ✓ The resulting state is consistent with the learned causal structure.")
# #     else:
# #         print("  ⚠ The resulting state may be inconsistent with the learned causal structure.")
# #     print(f"\n  Causal distance : {float(result.d_causal):.3f}")
# #     print(f"  Causal sparsity : {float(result.sparsity):.2f}")
# #     print(f"  Runtime         : {float(result.runtime):.3f} sec")

# #     changed = result.changed or []
# #     downstream = [j for j in changed if j not in direct]
# #     total_features = len(result.x_obs)
# #     violation = float(result.violation)

# #     metrics = [
# #         {
# #             "title": "DIRECT INTERVENTIONS",
# #             "value": f"{len(direct)} / {total_features}",
# #             "explanation": "Features intentionally changed\nto obtain the counterfactual.",
# #         },
# #         {
# #             "title": "DOWNSTREAM CHANGES",
# #             "value": str(len(downstream)),
# #             "explanation": "Additional features that changed\nbecause of causal propagation.",
# #         },
# #         {
# #             "title": "CAUSAL SPARSITY",
# #             "value": f"{float(result.sparsity) * 100:.1f}%",
# #             "explanation": "How concentrated the solution is.\nHigher means fewer direct changes.",
# #         },
# #         {
# #             "title": "CAUSAL CONSISTENCY",
# #             "value": "✓ Consistent" if violation < 1.5 else "⚠ Check",
# #             "explanation": f"Constraint score: {violation:.4f}\nLower indicates better consistency.",
# #         },
# #         {
# #             "title": "CAUSAL DISTANCE",
# #             "value": f"{float(result.d_causal):.4f}",
# #             "explanation": "Distance of the counterfactual\nfrom the observed causal state.",
# #         },
# #         {
# #             "title": "RUNTIME",
# #             "value": f"{float(result.runtime):.2f} s",
# #             "explanation": "Time required to find\nthe counterfactual.",
# #         },
# #     ]
# #     _show_metric_cards(metrics)

# #     print("\nDIRECT INTERVENTIONS")
# #     _line()
# #     if direct:
# #         rows = []
# #         for j in direct:
# #             old = float(result.x_obs[j])
# #             new = float(result.x_star[j])
# #             rows.append([
# #                 names[j], f"{old:.4f}", f"{new:.4f}",
# #                 f"{new - old:+.4f}", _format_change(old, new),
# #             ])
# #         _show_table(
# #             rows,
# #             ["Feature", "Current", "New value", "Change", "Required action"],
# #             title="Direct causal interventions",
# #             figsize=(12, max(3, 2 + 0.45 * len(rows))),
# #         )
# #     else:
# #         print("  No direct feature intervention.")

# #     print("\nDOWNSTREAM EFFECTS")
# #     _line()
# #     if downstream:
# #         print(f"  {len(downstream)} feature(s) changed as a consequence of the direct intervention.")
# #         rows = []
# #         for j in downstream:
# #             old = float(result.x_obs[j])
# #             new = float(result.x_star[j])
# #             rows.append([names[j], f"{old:.4f}", f"{new:.4f}", f"{new - old:+.4f}"])
# #         _show_table(
# #             rows,
# #             ["Feature", "Original", "Causal result", "Change"],
# #             title="Downstream causal changes",
# #             figsize=(10, max(3, 2 + 0.45 * len(rows))),
# #         )
# #     else:
# #         print("  No downstream feature changes.")
# #     print()


# # # ================================================================
# # # 3. CAUSAL FEATURE IMPACT / CAI
# # # ================================================================


# # def show_attribution(result: CAIResult, feature_names=None):
# #     """Display the complete CAI table, uncertainty, and main causal driver."""
# #     names = _names(result.x_obs, feature_names)
# #     cai = np.asarray(result.cai, dtype=float)
# #     if cai.size == 0:
# #         _header("CAUSAL FEATURE IMPACT")
# #         print("\n  No CAI values available.")
# #         return None

# #     order = np.argsort(np.abs(cai))[::-1]
# #     top = int(order[0])
# #     top_effect = float(cai[top])

# #     _header("CAUSAL FEATURE IMPACT")
# #     print(
# #         "\nThe causal effect estimates how intervening on each feature "
# #         "changes the expected model output."
# #     )
# #     if result.n_samples is not None:
# #         print(f"\n  Monte Carlo samples : {result.n_samples}")

# #     print("\nFeature-level causal effects")
# #     _line()
# #     rows = []
# #     for rank, j in enumerate(order):
# #         j = int(j)
# #         intervention = _value_at(result.intervention_values, j)
# #         if intervention is None:
# #             intervention = float(result.x_obs[j])
# #         f_do = _value_at(result.f_do, j)
# #         effect = float(cai[j])
# #         se = _value_at(result.standard_errors, j)
# #         ci = None
# #         if result.confidence_intervals is not None:
# #             try:
# #                 ci = _format_ci(result.confidence_intervals[j])
# #             except Exception:
# #                 ci = None
# #         rows.append([
# #             rank + 1,
# #             names[j],
# #             f"{intervention:.4f}" if intervention is not None else "-",
# #             f"{f_do:.4f}" if f_do is not None else "-",
# #             f"{effect:+.4f}",
# #             f"{se:.4f}" if se is not None else "-",
# #             ci if ci is not None else "-",
# #             _effect_description(effect),
# #         ])

# #     _show_table(
# #         rows,
# #         [
# #             "Rank", "Feature", "Intervention", "E[f | do]", "CAI",
# #             "SE", "95% CI", "Interpretation",
# #         ],
# #         title="Feature-level causal effects",
# #         figsize=(15, max(4, min(16, 1.5 + 0.40 * len(rows)))),
# #         font_size=8,
# #     )

# #     print("\nMain causal driver")
# #     _line()
# #     print(f"  {_direction_sentence(names[top], top_effect)}")
# #     print(f"  CAI : {top_effect:+.4f}")
# #     print(f"  Baseline expected output : {float(result.baseline):.4f}")
# #     print()


# # # ================================================================
# # # 4. UNIFIED EXPLANATION
# # # ================================================================


# # def show_explanation(explanation: UnifiedExplanation, feature_names=None):
# #     """Display the complete high-level CAUSE-XAI explanation."""
# #     names = _names(explanation.x_obs, feature_names)
# #     cce = explanation.cce
# #     cai = explanation.cai
# #     cai_values = np.asarray(cai.cai, dtype=float)

# #     if cai_values.size == 0:
# #         _header("CAUSE-XAI — MODEL EXPLANATION")
# #         print("\n  No causal attribution values available.")
# #         return

# #     order = np.argsort(np.abs(cai_values))[::-1]
# #     top = int(order[0])
# #     top_effect = float(cai_values[top])
# #     direct = cce.direct_interventions or []
# #     changed = cce.changed or []
# #     downstream = [j for j in changed if j not in direct]

# #     _header("CAUSE-XAI — MODEL EXPLANATION")

# #     print("\n1. Prediction")
# #     _line()
# #     print(f"  Current output : {float(explanation.y_fact):.4f}")
# #     print(f"  Target output  : {float(explanation.y_foil):.4f}")
# #     print(f"  Achieved output: {float(cce.y_achieved):.4f}")
# #     if cce.feasible:
# #         print("\n  ✓ A feasible causal counterfactual was found.")
# #     else:
# #         print("\n  ✗ The requested target could not be reached.")

# #     print("\n2. Top causal factors")
# #     _line()
# #     rows = []
# #     for rank, j in enumerate(order[:min(5, len(order))]):
# #         j = int(j)
# #         effect = float(cai_values[j])
# #         rows.append([
# #             rank + 1,
# #             names[j],
# #             f"{effect:+.4f}",
# #             _effect_description(effect),
# #         ])
# #     _show_table(
# #         rows,
# #         ["Rank", "Feature", "CAI", "Interpretation"],
# #         title="Top causal factors",
# #         figsize=(10, max(3.5, 1.8 + 0.55 * len(rows))),
# #     )

# #     print("\n3. What would need to change?")
# #     _line()
# #     if direct:
# #         rows = []
# #         for j in direct:
# #             old = float(cce.x_obs[j])
# #             new = float(cce.x_star[j])
# #             rows.append([
# #                 "★", names[j], f"{old:.4f}", f"{new:.4f}",
# #                 f"{new - old:+.4f}", _format_change(old, new),
# #             ])
# #         _show_table(
# #             rows,
# #             ["", "Feature", "Current", "Required", "Δ", "Action"],
# #             title="Direct causal actions",
# #             figsize=(11, max(3, 2 + 0.5 * len(rows))),
# #         )
# #     else:
# #         print("  No direct causal intervention was identified.")

# #     print("\n4. Causal validity")
# #     _line()
# #     if float(cce.violation) < 1.5:
# #         print("  ✓ The counterfactual remains consistent with the learned causal structure.")
# #     else:
# #         print("  ⚠ The counterfactual may violate the learned causal structure.")
# #     print(f"  Causal distance : {float(cce.d_causal):.4f}")
# #     print(f"  Causal sparsity : {float(cce.sparsity):.2f}")
# #     print(f"  Runtime         : {float(cce.runtime):.3f} sec")

# #     if downstream:
# #         print("\n5. Causal propagation")
# #         _line()
# #         print(f"  {len(downstream)} feature(s) changed as a consequence of the direct intervention.")
# #         print("  These are consequences of the causal structure, not additional user actions.")
# #         rows = []
# #         for j in downstream:
# #             old = float(cce.x_obs[j])
# #             new = float(cce.x_star[j])
# #             rows.append([names[j], f"{old:.4f}", f"{new:.4f}", f"{new - old:+.4f}"])
# #         _show_table(
# #             rows,
# #             ["Feature", "Original", "After propagation", "Change"],
# #             title="Downstream causal effects",
# #             figsize=(10, max(3, 2 + 0.45 * len(rows))),
# #         )
# #     else:
# #         print("\n5. Causal propagation")
# #         _line()
# #         print("  No downstream causal changes.")

# #     print("\n6. Causal quality")
# #     _line()
# #     metrics = [
# #         {
# #             "title": "DIRECT CHANGES",
# #             "value": f"{len(direct)} / {len(explanation.x_obs)}",
# #             "explanation": "Features deliberately changed\nto obtain the target.",
# #         },
# #         {
# #             "title": "DOWNSTREAM EFFECTS",
# #             "value": str(len(downstream)),
# #             "explanation": "Features that changed because\nof causal propagation.",
# #         },
# #         {
# #             "title": "CAUSAL SPARSITY",
# #             "value": f"{float(cce.sparsity) * 100:.1f}%",
# #             "explanation": "Higher means fewer direct changes.",
# #         },
# #         {
# #             "title": "CAUSAL CONSISTENCY",
# #             "value": "✓ Consistent" if float(cce.violation) < 1.5 else "⚠ Check",
# #             "explanation": f"Constraint score: {float(cce.violation):.4f}",
# #         },
# #         {
# #             "title": "CAUSAL DISTANCE",
# #             "value": f"{float(cce.d_causal):.4f}",
# #             "explanation": "Distance from observed causal state.",
# #         },
# #         {
# #             "title": "RUNTIME",
# #             "value": f"{float(cce.runtime):.2f} s",
# #             "explanation": "Time required to compute the explanation.",
# #         },
# #     ]
# #     _show_metric_cards(metrics)

# #     print("\n7. Conclusion")
# #     _line()
# #     print(f"  {_direction_sentence(names[top], top_effect)}")
# #     if cce.feasible:
# #         print(
# #             f"\n  A causal intervention changes the model output from "
# #             f"{float(cce.y_fact):.4f} to {float(cce.y_achieved):.4f}."
# #         )
# #     else:
# #         print(
# #             f"\n  The requested target {float(cce.y_foil):.4f} could not be reached "
# #             "under the learned causal constraints."
# #         )
# #     print()


# # # ================================================================
# # # 5. CAI VS SHAP
# # # ================================================================


# # def show_cai_vs_shap(comparison: dict, feature_names=None):
# #     """Display CAI vs SHAP-style interpretation, plots, and comparison table."""
# #     if not isinstance(comparison, dict):
# #         raise TypeError("comparison must be a dictionary.")

# #     required = {"cai", "shap_style", "baseline_int", "baseline_obs"}
# #     missing = [key for key in required if key not in comparison]
# #     if missing:
# #         raise KeyError("CAI vs SHAP comparison is missing: " + ", ".join(missing))

# #     cai = np.asarray(comparison["cai"], dtype=float)
# #     shap = np.asarray(comparison["shap_style"], dtype=float)
# #     if cai.shape != shap.shape:
# #         raise ValueError("CAI and SHAP arrays must have the same shape.")

# #     names = _names(cai, feature_names)
# #     difference = cai - shap
# #     order = np.argsort(np.abs(difference))[::-1]
# #     bias_threshold = 0.05

# #     _header("CAUSAL vs OBSERVATIONAL ATTRIBUTION")

# #     print("\nCAI")
# #     _line()
# #     print("  Measures the change in expected model output under an active feature intervention.")

# #     print("\nSHAP-style")
# #     _line()
# #     print("  Describes feature contribution using observational relationships.")

# #     print("\nWhy compare them?")
# #     _line()
# #     print(
# #         "  Large disagreement means that the feature's observational contribution "
# #         "differs from its estimated interventional effect."
# #     )

# #     print("\nREFERENCE OUTPUTS")
# #     _line()
# #     print(f"  Interventional baseline : {float(comparison['baseline_int']):.4f}")
# #     print(f"  Observational baseline  : {float(comparison['baseline_obs']):.4f}")

# #     plt = _get_plt()

# #     fig, ax = plt.subplots(figsize=(8, 5))
# #     ax.scatter(shap, cai, s=42)
# #     minimum = min(float(np.min(shap)), float(np.min(cai)))
# #     maximum = max(float(np.max(shap)), float(np.max(cai)))
# #     padding = (maximum - minimum) * 0.08 + 1e-6
# #     ax.plot(
# #         [minimum - padding, maximum + padding],
# #         [minimum - padding, maximum + padding],
# #         linestyle="--", linewidth=1.5,
# #     )
# #     for i in range(len(names)):
# #         ax.annotate(
# #             names[i], (shap[i], cai[i]), fontsize=7,
# #             xytext=(4, 4), textcoords="offset points",
# #         )
# #     ax.set_xlabel("SHAP-style attribution")
# #     ax.set_ylabel("CAI")
# #     ax.set_title("CAI vs SHAP-style attribution", fontweight="bold")
# #     ax.grid(alpha=0.2)
# #     plt.tight_layout()
# #     plt.show()

# #     sorted_names = [names[int(j)] for j in order]
# #     sorted_difference = [float(difference[int(j)]) for j in order]
# #     fig, ax = plt.subplots(figsize=(10, max(5, 0.35 * len(order))))
# #     y = np.arange(len(order))
# #     ax.barh(y, sorted_difference)
# #     ax.axvline(0, linewidth=1)
# #     ax.set_yticks(y)
# #     ax.set_yticklabels(sorted_names)
# #     ax.invert_yaxis()
# #     ax.set_xlabel("CAI − SHAP-style")
# #     ax.set_title("Where CAI and SHAP-style attribution disagree", fontweight="bold")
# #     plt.tight_layout()
# #     plt.show()

# #     print("\nDETAILED COMPARISON")
# #     _line()
# #     rows = []
# #     n_biased = 0
# #     for rank, j in enumerate(order):
# #         j = int(j)
# #         diff = float(difference[j])
# #         biased = abs(diff) > bias_threshold
# #         if biased:
# #             n_biased += 1
# #         rows.append([
# #             rank + 1,
# #             names[j],
# #             f"{cai[j]:+.4f}",
# #             f"{shap[j]:+.4f}",
# #             f"{diff:+.4f}",
# #             "⚠" if biased else "✓",
# #         ])

# #     _show_table(
# #         rows,
# #         ["Rank", "Feature", "CAI", "SHAP", "Difference", "Flag"],
# #         title="CAI vs SHAP-style comparison",
# #         figsize=(11, max(4, min(15, 1.5 + 0.35 * len(rows)))),
# #         font_size=8,
# #     )

# #     print(f"\n  Features with |CAI − SHAP| > {bias_threshold:.2f}: {n_biased}/{len(cai)}")
# #     if len(order):
# #         largest = int(order[0])
# #         print("\nLARGEST DISAGREEMENT")
# #         _line()
# #         print(f"  Feature    : {names[largest]}")
# #         print(f"  CAI        : {cai[largest]:+.4f}")
# #         print(f"  SHAP       : {shap[largest]:+.4f}")
# #         print(f"  Difference : {difference[largest]:+.4f}")
# #     print()


# # # ================================================================
# # # 6. DAG DISPLAY
# # # ================================================================


# # def show_dag(model, feature_names=None):
# #     """Create a Graphviz representation of the learned DAG with roots highlighted."""
# #     try:
# #         from graphviz import Digraph
# #     except ImportError as exc:
# #         raise ImportError(
# #             "DAG visualization requires the Python graphviz package.\n"
# #             "Install with:\n"
# #             "    pip install graphviz"
# #         ) from exc

# #     adj = np.asarray(model._adj)
# #     p = adj.shape[0]
# #     names = list(feature_names) if feature_names is not None else [f"X{i + 1}" for i in range(p)]

# #     dot = Digraph("CAUSE_XAI_DAG")
# #     dot.attr(
# #         rankdir="LR",
# #         splines="ortho",
# #         nodesep="0.30",
# #         ranksep="0.55",
# #         bgcolor="white",
# #     )
# #     dot.attr(
# #         "node",
# #         shape="box",
# #         style="rounded",
# #         fontsize="9",
# #         margin="0.08",
# #     )
# #     dot.attr("edge", arrowsize="0.55", penwidth="0.9")

# #     for i, name in enumerate(names):
# #         has_parent = bool(np.any(adj[:, i]))
# #         has_child = bool(np.any(adj[i, :]))
# #         is_root = not has_parent
# #         is_sink = not has_child

# #         if is_root:
# #             label = f"{name}\\n(ROOT)"
# #             dot.node(
# #                 str(i), label,
# #                 style="rounded,filled",
# #                 fillcolor="lightyellow",
# #                 penwidth="2.0",
# #             )
# #         elif is_sink:
# #             label = f"{name}\\n(sink)"
# #             dot.node(str(i), label)
# #         else:
# #             dot.node(str(i), name)

# #     for i in range(p):
# #         for j in range(p):
# #             if adj[i, j] != 0:
# #                 dot.edge(str(i), str(j))

# #     return dot


# # # ================================================================
# # # 7. GENERIC DISPLAY
# # # ================================================================


# # def display(result, feature_names=None):
# #     """Automatically select the appropriate CAUSE-XAI display."""
# #     if isinstance(result, UnifiedExplanation):
# #         return show_explanation(result, feature_names=feature_names)
# #     if isinstance(result, CCEResult):
# #         return show_counterfactual(result, feature_names=feature_names)
# #     if isinstance(result, CAIResult):
# #         return show_attribution(result, feature_names=feature_names)
# #     if isinstance(result, dict):
# #         if "cai" in result and "shap_style" in result:
# #             return show_cai_vs_shap(result, feature_names=feature_names)
# #         raise TypeError("Dictionary does not contain a recognised CAUSE-XAI result.")
# #     raise TypeError(f"Unsupported result type: {type(result).__name__}")


# # __all__ = [
# #     "show_fit",
# #     "show_counterfactual",
# #     "show_attribution",
# #     "show_explanation",
# #     "show_cai_vs_shap",
# #     "show_dag",
# #     "display",
# # ]

# import numpy as np

# from .results import CCEResult, CAIResult, UnifiedExplanation


# def _get_plt():
#     try:
#         import matplotlib.pyplot as plt
#         return plt
#     except ImportError as exc:
#         raise ImportError(
#             "CAUSE-XAI graphical displays require matplotlib.\n"
#             "Install it with:\n"
#             "    pip install matplotlib"
#         ) from exc


# def _names(values, feature_names=None):
#     n = len(values)
#     if feature_names is not None:
#         if len(feature_names) != n:
#             raise ValueError(
#                 "feature_names must have the same length as the number of features."
#             )
#         return list(feature_names)
#     return [f"Feature {i + 1}" for i in range(n)]


# def _line(char="─", width=78):
#     print(char * width)


# def _header(title, width=78):
#     print()
#     print("═" * width)
#     print(title.center(width))
#     print("═" * width)


# def _format_change(old, new):
#     delta = float(new) - float(old)
#     if abs(delta) < 1e-10:
#         return "No change"
#     if delta > 0:
#         return f"Increase by {abs(delta):.3f}"
#     return f"Decrease by {abs(delta):.3f}"


# def _format_ci(ci):
#     return f"[{float(ci[0]):+.4f}, {float(ci[1]):+.4f}]"


# def _effect_description(effect):
#     effect = float(effect)
#     if abs(effect) < 1e-10:
#         return "Little measurable influence"
#     magnitude = abs(effect)
#     if effect > 0:
#         if magnitude >= 0.20:
#             return "Strong increase"
#         if magnitude >= 0.10:
#             return "Moderate increase"
#         return "Small increase"
#     if magnitude >= 0.20:
#         return "Strong decrease"
#     if magnitude >= 0.10:
#         return "Moderate decrease"
#     return "Small decrease"


# def _direction_sentence(feature, effect):
#     effect = float(effect)
#     if effect > 0:
#         return (
#             f"{feature} has the strongest estimated causal influence "
#             f"and increases the expected model output."
#         )
#     if effect < 0:
#         return (
#             f"{feature} has the strongest estimated causal influence "
#             f"and decreases the expected model output."
#         )
#     return (
#         f"{feature} has little measurable causal influence "
#         f"on the expected model output."
#     )


# def _show_table(rows, columns, title=None, figsize=None, font_size=9):
#     plt = _get_plt()
#     if figsize is None:
#         figsize = (
#             max(9, len(columns) * 1.5),
#             max(2.5, min(14, 1.0 + 0.42 * len(rows))),
#         )

#     fig, ax = plt.subplots(figsize=figsize)
#     ax.axis("off")
#     if title is not None:
#         ax.set_title(title, fontsize=13, pad=16, fontweight="bold")

#     table = ax.table(
#         cellText=rows,
#         colLabels=columns,
#         loc="center",
#         cellLoc="center",
#     )
#     table.auto_set_font_size(False)
#     table.set_fontsize(font_size)
#     table.scale(1, 1.6)
#     plt.tight_layout()
#     plt.show()
#     return fig


# def _show_metric_cards(metrics):
#     plt = _get_plt()
#     n = len(metrics)
#     cols = 3
#     rows = int(np.ceil(n / cols))
#     fig = plt.figure(figsize=(13, 3.0 * rows))

#     for i, metric in enumerate(metrics):
#         ax = fig.add_subplot(rows, cols, i + 1)
#         ax.axis("off")
#         ax.text(
#             0.5, 0.76, metric["title"], ha="center", va="center",
#             fontsize=10, fontweight="bold",
#         )
#         ax.text(
#             0.5, 0.50, metric["value"], ha="center", va="center",
#             fontsize=22, fontweight="bold",
#         )
#         ax.text(
#             0.5, 0.19, metric["explanation"], ha="center", va="center",
#             fontsize=8.5, wrap=True,
#         )
#         for spine in ax.spines.values():
#             spine.set_visible(True)

#     for i in range(n, rows * cols):
#         ax = fig.add_subplot(rows, cols, i + 1)
#         ax.axis("off")

#     plt.tight_layout()
#     plt.show()
#     return fig


# def _show_prediction_transition(current, achieved, target=None, title="Prediction change"):
#     plt = _get_plt()
#     current = float(current)
#     achieved = float(achieved)
#     fig, ax = plt.subplots(figsize=(11, 3.8))

#     minimum = min(current, achieved)
#     maximum = max(current, achieved)
#     span = max(abs(maximum - minimum), 1e-6)
#     ax.set_xlim(minimum - 0.15 * span, maximum + 0.15 * span)
#     ax.set_ylim(-0.8, 0.8)
#     ax.axhline(0, linewidth=2)
#     ax.scatter([current], [0], s=120, zorder=5)
#     ax.scatter([achieved], [0], s=120, zorder=5)
#     ax.annotate(
#         f"Current\n{current:.4f}", xy=(current, 0), xytext=(current, 0.45),
#         ha="center", arrowprops=dict(arrowstyle="->"),
#     )
#     ax.annotate(
#         f"After change\n{achieved:.4f}", xy=(achieved, 0),
#         xytext=(achieved, -0.50), ha="center",
#         arrowprops=dict(arrowstyle="->"),
#     )
#     ax.annotate(
#         "", xy=(achieved, 0), xytext=(current, 0),
#         arrowprops=dict(arrowstyle="<->", linewidth=2),
#     )
#     ax.text(
#         (current + achieved) / 2, 0.13, f"Change: {achieved - current:+.4f}",
#         ha="center", fontsize=10, fontweight="bold",
#     )
#     if target is not None:
#         target = float(target)
#         ax.axvline(target, linestyle="--", linewidth=1.5)
#         ax.text(target, 0.68, f"Target\n{target:.4f}", ha="center", fontsize=8)
#     ax.set_title(title, fontsize=13, fontweight="bold")
#     ax.set_yticks([])
#     ax.set_xlabel("Model output")
#     plt.tight_layout()
#     plt.show()
#     return fig


# def _value_at(values, index):
#     if values is None:
#         return None
#     try:
#         return float(values[index])
#     except Exception:
#         try:
#             return float(np.asarray(values).reshape(-1)[index])
#         except Exception:
#             return None


# # ================================================================
# # 1. FIT DISPLAY
# # ================================================================


# def show_fit(model, feature_names=None, verbose=False):
#     """Display model readiness, learned structure, and the learned DAG."""
#     _header("CAUSE-XAI — MODEL READY")

#     print("\nStatus")
#     _line()
#     print("  ✓ Causal structure discovered")
#     print("  ✓ Causal mechanisms fitted")
#     print("  ✓ Model ready for explanation")

#     adj = getattr(model, "_adj", None)
#     if adj is None:
#         adj = getattr(model, "adj_", None)
#     if adj is None:
#         print("\nCausal structure information is unavailable.")
#         return None

#     adj = np.asarray(adj)
#     p = adj.shape[0]
#     names = list(feature_names) if feature_names is not None else [f"X{i + 1}" for i in range(p)]

#     edges = [(i, j) for i in range(p) for j in range(p) if adj[i, j] != 0]
#     parents = {j: [] for j in range(p)}
#     children = {i: [] for i in range(p)}
#     for i, j in edges:
#         children[i].append(j)
#         parents[j].append(i)

#     roots = [names[i] for i in range(p) if not parents[i]]
#     sinks = [names[i] for i in range(p) if not children[i]]

#     print("\nCausal structure")
#     _line()
#     print(f"  Variables                : {p}")
#     print(f"  Relationships discovered : {len(edges)}")
#     print(f"  Root variables           : {len(roots)}")
#     print(f"  Sink variables           : {len(sinks)}")

#     if roots:
#         print(f"  Roots                    : {', '.join(roots)}")

#     print("\nDAG")
#     _line()
#     print("  Root variables are highlighted in the graph.")

#     try:
#         dag = show_dag(model, feature_names=names)
#         if dag is not None:
#             try:
#                 from IPython.display import display as ipy_display
#                 ipy_display(dag)
#             except Exception:
#                 try:
#                     dag.view()
#                 except Exception:
#                     print("\n  DAG object created successfully.")
#         return dag
#     except Exception as exc:
#         print(f"\n  DAG visualization unavailable: {exc}")
#         return None


# # ================================================================
# # 2. COUNTERFACTUAL DISPLAY
# # ================================================================


# def show_counterfactual(result: CCEResult, feature_names=None):
#     """Display the user-facing causal counterfactual and its causal diagnostics."""
#     names = _names(result.x_obs, feature_names)
#     _header("COUNTERFACTUAL EXPLANATION")

#     print("\nWhat would need to change?")
#     _line()
#     direct = result.direct_interventions or []

#     if result.feasible and direct:
#         for j in direct:
#             old = float(result.x_obs[j])
#             new = float(result.x_star[j])
#             print(f"\n  {names[j]}")
#             print(f"    Current value : {old:.3f}")
#             print(f"    New value     : {new:.3f}")
#             print(f"    Required      : {_format_change(old, new).lower()}")
#     elif result.feasible and result.changed:
#         for j in result.changed:
#             old = float(result.x_obs[j])
#             new = float(result.x_star[j])
#             print(f"\n  {names[j]}")
#             print(f"    Current value : {old:.3f}")
#             print(f"    New value     : {new:.3f}")
#             print(f"    Required      : {_format_change(old, new).lower()}")
#     else:
#         print("  No feasible feature change was found under the current causal constraints.")

#     print("\nCausal validity")
#     _line()
#     if float(result.violation) < 1.5:
#         print("  ✓ The resulting state is consistent with the learned causal structure.")
#     else:
#         print("  ⚠ The resulting state may be inconsistent with the learned causal structure.")
#     print(f"\n  Causal distance : {float(result.d_causal):.3f}")
#     print(f"  Causal sparsity : {float(result.sparsity):.2f}")
#     print(f"  Runtime         : {float(result.runtime):.3f} sec")

#     changed = result.changed or []
#     downstream = [j for j in changed if j not in direct]
#     total_features = len(result.x_obs)
#     violation = float(result.violation)

#     metrics = [
#         {
#             "title": "DIRECT INTERVENTIONS",
#             "value": f"{len(direct)} / {total_features}",
#             "explanation": "Features intentionally changed\nto obtain the counterfactual.",
#         },
#         {
#             "title": "DOWNSTREAM CHANGES",
#             "value": str(len(downstream)),
#             "explanation": "Additional features that changed\nbecause of causal propagation.",
#         },
#         {
#             "title": "CAUSAL SPARSITY",
#             "value": f"{float(result.sparsity) * 100:.1f}%",
#             "explanation": "How concentrated the solution is.\nHigher means fewer direct changes.",
#         },
#         {
#             "title": "CAUSAL CONSISTENCY",
#             "value": "✓ Consistent" if violation < 1.5 else "⚠ Check",
#             "explanation": f"Constraint score: {violation:.4f}\nLower indicates better consistency.",
#         },
#         {
#             "title": "CAUSAL DISTANCE",
#             "value": f"{float(result.d_causal):.4f}",
#             "explanation": "Distance of the counterfactual\nfrom the observed causal state.",
#         },
#         {
#             "title": "RUNTIME",
#             "value": f"{float(result.runtime):.2f} s",
#             "explanation": "Time required to find\nthe counterfactual.",
#         },
#     ]
#     _show_metric_cards(metrics)

#     print("\nDIRECT INTERVENTIONS")
#     _line()
#     if direct:
#         rows = []
#         for j in direct:
#             old = float(result.x_obs[j])
#             new = float(result.x_star[j])
#             rows.append([
#                 names[j], f"{old:.4f}", f"{new:.4f}",
#                 f"{new - old:+.4f}", _format_change(old, new),
#             ])
#         _show_table(
#             rows,
#             ["Feature", "Current", "New value", "Change", "Required action"],
#             title="Direct causal interventions",
#             figsize=(12, max(3, 2 + 0.45 * len(rows))),
#         )
#     else:
#         print("  No direct feature intervention.")

#     print("\nDOWNSTREAM EFFECTS")
#     _line()
#     if downstream:
#         print(f"  {len(downstream)} feature(s) changed as a consequence of the direct intervention.")
#         rows = []
#         for j in downstream:
#             old = float(result.x_obs[j])
#             new = float(result.x_star[j])
#             rows.append([names[j], f"{old:.4f}", f"{new:.4f}", f"{new - old:+.4f}"])
#         _show_table(
#             rows,
#             ["Feature", "Original", "Causal result", "Change"],
#             title="Downstream causal changes",
#             figsize=(10, max(3, 2 + 0.45 * len(rows))),
#         )
#     else:
#         print("  No downstream feature changes.")
#     print()


# # ================================================================
# # 3. CAUSAL FEATURE IMPACT / CAI
# # ================================================================


# def show_attribution(result: CAIResult, feature_names=None):
#     """Display the complete CAI table, uncertainty, and main causal driver."""
#     names = _names(result.x_obs, feature_names)
#     cai = np.asarray(result.cai, dtype=float)
#     if cai.size == 0:
#         _header("CAUSAL FEATURE IMPACT")
#         print("\n  No CAI values available.")
#         return None

#     order = np.argsort(np.abs(cai))[::-1]
#     top = int(order[0])
#     top_effect = float(cai[top])

#     _header("CAUSAL FEATURE IMPACT")
#     print(
#         "\nThe causal effect estimates how intervening on each feature "
#         "changes the expected model output."
#     )
#     if result.n_samples is not None:
#         print(f"\n  Monte Carlo samples : {result.n_samples}")

#     print("\nFeature-level causal effects")
#     _line()
#     rows = []
#     for rank, j in enumerate(order):
#         j = int(j)
#         intervention = _value_at(result.intervention_values, j)
#         if intervention is None:
#             intervention = float(result.x_obs[j])
#         f_do = _value_at(result.f_do, j)
#         effect = float(cai[j])
#         se = _value_at(result.standard_errors, j)
#         ci = None
#         if result.confidence_intervals is not None:
#             try:
#                 ci = _format_ci(result.confidence_intervals[j])
#             except Exception:
#                 ci = None
#         rows.append([
#             rank + 1,
#             names[j],
#             f"{intervention:.4f}" if intervention is not None else "-",
#             f"{f_do:.4f}" if f_do is not None else "-",
#             f"{effect:+.4f}",
#             f"{se:.4f}" if se is not None else "-",
#             ci if ci is not None else "-",
#             _effect_description(effect),
#         ])

#     _show_table(
#         rows,
#         [
#             "Rank", "Feature", "Intervention", "E[f | do]", "CAI",
#             "SE", "95% CI", "Interpretation",
#         ],
#         title="Feature-level causal effects",
#         figsize=(15, max(4, min(16, 1.5 + 0.40 * len(rows)))),
#         font_size=8,
#     )

#     print("\nMain causal driver")
#     _line()
#     print(f"  {_direction_sentence(names[top], top_effect)}")
#     print(f"  CAI : {top_effect:+.4f}")
#     print(f"  Baseline expected output : {float(result.baseline):.4f}")
#     print()


# # ================================================================
# # 4. UNIFIED EXPLANATION
# # ================================================================


# def show_explanation(explanation: UnifiedExplanation, feature_names=None):
#     """Display the complete high-level CAUSE-XAI explanation."""
#     names = _names(explanation.x_obs, feature_names)
#     cce = explanation.cce
#     cai = explanation.cai
#     cai_values = np.asarray(cai.cai, dtype=float)

#     if cai_values.size == 0:
#         _header("CAUSE-XAI — MODEL EXPLANATION")
#         print("\n  No causal attribution values available.")
#         return

#     order = np.argsort(np.abs(cai_values))[::-1]
#     top = int(order[0])
#     top_effect = float(cai_values[top])
#     direct = cce.direct_interventions or []
#     changed = cce.changed or []
#     downstream = [j for j in changed if j not in direct]

#     _header("CAUSE-XAI — MODEL EXPLANATION")

#     print("\n1. Prediction")
#     _line()
#     print(f"  Current output : {float(explanation.y_fact):.4f}")
#     print(f"  Target output  : {float(explanation.y_foil):.4f}")
#     print(f"  Achieved output: {float(cce.y_achieved):.4f}")
#     if cce.feasible:
#         print("\n  ✓ A feasible causal counterfactual was found.")
#     else:
#         print("\n  ✗ The requested target could not be reached.")

#     print("\n2. Top causal factors")
#     _line()
#     rows = []
#     for rank, j in enumerate(order[:min(5, len(order))]):
#         j = int(j)
#         effect = float(cai_values[j])
#         rows.append([
#             rank + 1,
#             names[j],
#             f"{effect:+.4f}",
#             _effect_description(effect),
#         ])
#     _show_table(
#         rows,
#         ["Rank", "Feature", "CAI", "Interpretation"],
#         title="Top causal factors",
#         figsize=(10, max(3.5, 1.8 + 0.55 * len(rows))),
#     )

#     print("\n3. What would need to change?")
#     _line()
#     if direct:
#         rows = []
#         for j in direct:
#             old = float(cce.x_obs[j])
#             new = float(cce.x_star[j])
#             rows.append([
#                 "★", names[j], f"{old:.4f}", f"{new:.4f}",
#                 f"{new - old:+.4f}", _format_change(old, new),
#             ])
#         _show_table(
#             rows,
#             ["", "Feature", "Current", "Required", "Δ", "Action"],
#             title="Direct causal actions",
#             figsize=(11, max(3, 2 + 0.5 * len(rows))),
#         )
#     else:
#         print("  No direct causal intervention was identified.")

#     print("\n4. Causal validity")
#     _line()
#     if float(cce.violation) < 1.5:
#         print("  ✓ The counterfactual remains consistent with the learned causal structure.")
#     else:
#         print("  ⚠ The counterfactual may violate the learned causal structure.")
#     print(f"  Causal distance : {float(cce.d_causal):.4f}")
#     print(f"  Causal sparsity : {float(cce.sparsity):.2f}")
#     print(f"  Runtime         : {float(cce.runtime):.3f} sec")

#     if downstream:
#         print("\n5. Causal propagation")
#         _line()
#         print(f"  {len(downstream)} feature(s) changed as a consequence of the direct intervention.")
#         print("  These are consequences of the causal structure, not additional user actions.")
#         rows = []
#         for j in downstream:
#             old = float(cce.x_obs[j])
#             new = float(cce.x_star[j])
#             rows.append([names[j], f"{old:.4f}", f"{new:.4f}", f"{new - old:+.4f}"])
#         _show_table(
#             rows,
#             ["Feature", "Original", "After propagation", "Change"],
#             title="Downstream causal effects",
#             figsize=(10, max(3, 2 + 0.45 * len(rows))),
#         )
#     else:
#         print("\n5. Causal propagation")
#         _line()
#         print("  No downstream causal changes.")

#     print("\n6. Causal quality")
#     _line()
#     metrics = [
#         {
#             "title": "DIRECT CHANGES",
#             "value": f"{len(direct)} / {len(explanation.x_obs)}",
#             "explanation": "Features deliberately changed\nto obtain the target.",
#         },
#         {
#             "title": "DOWNSTREAM EFFECTS",
#             "value": str(len(downstream)),
#             "explanation": "Features that changed because\nof causal propagation.",
#         },
#         {
#             "title": "CAUSAL SPARSITY",
#             "value": f"{float(cce.sparsity) * 100:.1f}%",
#             "explanation": "Higher means fewer direct changes.",
#         },
#         {
#             "title": "CAUSAL CONSISTENCY",
#             "value": "✓ Consistent" if float(cce.violation) < 1.5 else "⚠ Check",
#             "explanation": f"Constraint score: {float(cce.violation):.4f}",
#         },
#         {
#             "title": "CAUSAL DISTANCE",
#             "value": f"{float(cce.d_causal):.4f}",
#             "explanation": "Distance from observed causal state.",
#         },
#         {
#             "title": "RUNTIME",
#             "value": f"{float(cce.runtime):.2f} s",
#             "explanation": "Time required to compute the explanation.",
#         },
#     ]
#     _show_metric_cards(metrics)

#     print("\n7. Conclusion")
#     _line()
#     print(f"  {_direction_sentence(names[top], top_effect)}")
#     if cce.feasible:
#         print(
#             f"\n  A causal intervention changes the model output from "
#             f"{float(cce.y_fact):.4f} to {float(cce.y_achieved):.4f}."
#         )
#     else:
#         print(
#             f"\n  The requested target {float(cce.y_foil):.4f} could not be reached "
#             "under the learned causal constraints."
#         )
#     print()


# # ================================================================
# # 5. CAI VS SHAP
# # ================================================================


# def show_cai_vs_shap(comparison: dict, feature_names=None):
#     """Display CAI vs SHAP-style interpretation, plots, and comparison table."""
#     if not isinstance(comparison, dict):
#         raise TypeError("comparison must be a dictionary.")

#     required = {"cai", "shap_style", "baseline_int", "baseline_obs"}
#     missing = [key for key in required if key not in comparison]
#     if missing:
#         raise KeyError("CAI vs SHAP comparison is missing: " + ", ".join(missing))

#     cai = np.asarray(comparison["cai"], dtype=float)
#     shap = np.asarray(comparison["shap_style"], dtype=float)
#     if cai.shape != shap.shape:
#         raise ValueError("CAI and SHAP arrays must have the same shape.")

#     names = _names(cai, feature_names)
#     difference = cai - shap
#     order = np.argsort(np.abs(difference))[::-1]
#     bias_threshold = 0.05

#     _header("CAUSAL vs OBSERVATIONAL ATTRIBUTION")

#     print("\nCAI")
#     _line()
#     print("  Measures the change in expected model output under an active feature intervention.")

#     print("\nSHAP-style")
#     _line()
#     print("  Describes feature contribution using observational relationships.")

#     print("\nWhy compare them?")
#     _line()
#     print(
#         "  Large disagreement means that the feature's observational contribution "
#         "differs from its estimated interventional effect."
#     )

#     print("\nREFERENCE OUTPUTS")
#     _line()
#     print(f"  Interventional baseline : {float(comparison['baseline_int']):.4f}")
#     print(f"  Observational baseline  : {float(comparison['baseline_obs']):.4f}")

#     plt = _get_plt()

#     fig, ax = plt.subplots(figsize=(8, 5))
#     ax.scatter(shap, cai, s=42)
#     minimum = min(float(np.min(shap)), float(np.min(cai)))
#     maximum = max(float(np.max(shap)), float(np.max(cai)))
#     padding = (maximum - minimum) * 0.08 + 1e-6
#     ax.plot(
#         [minimum - padding, maximum + padding],
#         [minimum - padding, maximum + padding],
#         linestyle="--", linewidth=1.5,
#     )
#     for i in range(len(names)):
#         ax.annotate(
#             names[i], (shap[i], cai[i]), fontsize=7,
#             xytext=(4, 4), textcoords="offset points",
#         )
#     ax.set_xlabel("SHAP-style attribution")
#     ax.set_ylabel("CAI")
#     ax.set_title("CAI vs SHAP-style attribution", fontweight="bold")
#     ax.grid(alpha=0.2)
#     plt.tight_layout()
#     plt.show()

#     sorted_names = [names[int(j)] for j in order]
#     sorted_difference = [float(difference[int(j)]) for j in order]
#     fig, ax = plt.subplots(figsize=(10, max(5, 0.35 * len(order))))
#     y = np.arange(len(order))
#     ax.barh(y, sorted_difference)
#     ax.axvline(0, linewidth=1)
#     ax.set_yticks(y)
#     ax.set_yticklabels(sorted_names)
#     ax.invert_yaxis()
#     ax.set_xlabel("CAI − SHAP-style")
#     ax.set_title("Where CAI and SHAP-style attribution disagree", fontweight="bold")
#     plt.tight_layout()
#     plt.show()

#     print("\nDETAILED COMPARISON")
#     _line()
#     rows = []
#     n_biased = 0
#     for rank, j in enumerate(order):
#         j = int(j)
#         diff = float(difference[j])
#         biased = abs(diff) > bias_threshold
#         if biased:
#             n_biased += 1
#         rows.append([
#             rank + 1,
#             names[j],
#             f"{cai[j]:+.4f}",
#             f"{shap[j]:+.4f}",
#             f"{diff:+.4f}",
#             "⚠" if biased else "✓",
#         ])

#     _show_table(
#         rows,
#         ["Rank", "Feature", "CAI", "SHAP", "Difference", "Flag"],
#         title="CAI vs SHAP-style comparison",
#         figsize=(11, max(4, min(15, 1.5 + 0.35 * len(rows)))),
#         font_size=8,
#     )

#     print(f"\n  Features with |CAI − SHAP| > {bias_threshold:.2f}: {n_biased}/{len(cai)}")
#     if len(order):
#         largest = int(order[0])
#         print("\nLARGEST DISAGREEMENT")
#         _line()
#         print(f"  Feature    : {names[largest]}")
#         print(f"  CAI        : {cai[largest]:+.4f}")
#         print(f"  SHAP       : {shap[largest]:+.4f}")
#         print(f"  Difference : {difference[largest]:+.4f}")
#     print()


# # ================================================================
# # 6. DAG DISPLAY
# # ================================================================


# def show_dag(model, feature_names=None):
#     """Create a Graphviz representation of the learned DAG with roots highlighted."""
#     try:
#         from graphviz import Digraph
#     except ImportError as exc:
#         raise ImportError(
#             "DAG visualization requires the Python graphviz package.\n"
#             "Install with:\n"
#             "    pip install graphviz"
#         ) from exc

#     adj = np.asarray(model._adj)
#     p = adj.shape[0]
#     names = list(feature_names) if feature_names is not None else [f"X{i + 1}" for i in range(p)]

#     dot = Digraph("CAUSE_XAI_DAG")
#     dot.attr(
#         rankdir="LR",
#         splines="ortho",
#         nodesep="0.30",
#         ranksep="0.55",
#         bgcolor="white",
#     )
#     dot.attr(
#         "node",
#         shape="box",
#         style="rounded",
#         fontsize="9",
#         margin="0.08",
#     )
#     dot.attr("edge", arrowsize="0.55", penwidth="0.9")

#     for i, name in enumerate(names):
#         has_parent = bool(np.any(adj[:, i]))
#         has_child = bool(np.any(adj[i, :]))
#         is_root = not has_parent
#         is_sink = not has_child

#         if is_root:
#             label = f"{name}\\n(ROOT)"
#             dot.node(
#                 str(i), label,
#                 style="rounded,filled",
#                 fillcolor="lightyellow",
#                 penwidth="2.0",
#             )
#         elif is_sink:
#             label = f"{name}\\n(sink)"
#             dot.node(str(i), label)
#         else:
#             dot.node(str(i), name)

#     for i in range(p):
#         for j in range(p):
#             if adj[i, j] != 0:
#                 dot.edge(str(i), str(j))

#     return dot


# # ================================================================
# # 7. GENERIC DISPLAY
# # ================================================================


# def display(result, feature_names=None):
#     """Automatically select the appropriate CAUSE-XAI display."""
#     if isinstance(result, UnifiedExplanation):
#         return show_explanation(result, feature_names=feature_names)
#     if isinstance(result, CCEResult):
#         return show_counterfactual(result, feature_names=feature_names)
#     if isinstance(result, CAIResult):
#         return show_attribution(result, feature_names=feature_names)
#     if isinstance(result, dict):
#         if "cai" in result and "shap_style" in result:
#             return show_cai_vs_shap(result, feature_names=feature_names)
#         raise TypeError("Dictionary does not contain a recognised CAUSE-XAI result.")
#     raise TypeError(f"Unsupported result type: {type(result).__name__}")


# __all__ = [
#     "show_fit",
#     "show_counterfactual",
#     "show_attribution",
#     "show_explanation",
#     "show_cai_vs_shap",
#     "show_dag",
#     "display",
# ]


import numpy as np

from .results import CCEResult, CAIResult, UnifiedExplanation


def _get_plt():
    try:
        import matplotlib.pyplot as plt
        return plt
    except ImportError as exc:
        raise ImportError(
            "CAUSE-XAI graphical displays require matplotlib.\n"
            "Install it with:\n"
            "    pip install matplotlib"
        ) from exc


def _names(values, feature_names=None):
    n = len(values)
    if feature_names is not None:
        if len(feature_names) != n:
            raise ValueError(
                "feature_names must have the same length as the number of features."
            )
        return list(feature_names)
    return [f"Feature {i + 1}" for i in range(n)]


def _line(char="─", width=78):
    print(char * width)


def _header(title, width=78):
    print()
    print("═" * width)
    print(title.center(width))
    print("═" * width)


def _format_change(old, new):
    delta = float(new) - float(old)
    if abs(delta) < 1e-10:
        return "No change"
    if delta > 0:
        return f"Increase by {abs(delta):.3f}"
    return f"Decrease by {abs(delta):.3f}"


def _format_ci(ci):
    return f"[{float(ci[0]):+.4f}, {float(ci[1]):+.4f}]"


def _effect_description(effect):
    effect = float(effect)
    if abs(effect) < 1e-10:
        return "Little measurable influence"
    magnitude = abs(effect)
    if effect > 0:
        if magnitude >= 0.20:
            return "Strong increase"
        if magnitude >= 0.10:
            return "Moderate increase"
        return "Small increase"
    if magnitude >= 0.20:
        return "Strong decrease"
    if magnitude >= 0.10:
        return "Moderate decrease"
    return "Small decrease"


def _direction_sentence(feature, effect):
    effect = float(effect)
    if effect > 0:
        return (
            f"{feature} has the strongest estimated causal influence "
            f"and increases the expected model output."
        )
    if effect < 0:
        return (
            f"{feature} has the strongest estimated causal influence "
            f"and decreases the expected model output."
        )
    return (
        f"{feature} has little measurable causal influence "
        f"on the expected model output."
    )


def _show_table(rows, columns, title=None, figsize=None, font_size=9):
    plt = _get_plt()
    if figsize is None:
        figsize = (
            max(9, len(columns) * 1.5),
            max(2.5, min(14, 1.0 + 0.42 * len(rows))),
        )

    fig, ax = plt.subplots(figsize=figsize)
    ax.axis("off")
    if title is not None:
        ax.set_title(title, fontsize=13, pad=16, fontweight="bold")

    table = ax.table(
        cellText=rows,
        colLabels=columns,
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(font_size)
    table.scale(1, 1.6)
    plt.tight_layout()
    plt.show()
    return fig


def _show_metric_cards(metrics):
    plt = _get_plt()
    n = len(metrics)
    cols = 3
    rows = int(np.ceil(n / cols))
    fig = plt.figure(figsize=(13, 3.0 * rows))

    for i, metric in enumerate(metrics):
        ax = fig.add_subplot(rows, cols, i + 1)
        ax.axis("off")
        ax.text(
            0.5, 0.76, metric["title"], ha="center", va="center",
            fontsize=10, fontweight="bold",
        )
        ax.text(
            0.5, 0.50, metric["value"], ha="center", va="center",
            fontsize=22, fontweight="bold",
        )
        ax.text(
            0.5, 0.19, metric["explanation"], ha="center", va="center",
            fontsize=8.5, wrap=True,
        )
        for spine in ax.spines.values():
            spine.set_visible(True)

    for i in range(n, rows * cols):
        ax = fig.add_subplot(rows, cols, i + 1)
        ax.axis("off")

    plt.tight_layout()
    plt.show()
    return fig


def _show_prediction_transition(current, achieved, target=None, title="Prediction change"):
    plt = _get_plt()
    current = float(current)
    achieved = float(achieved)
    fig, ax = plt.subplots(figsize=(11, 3.8))

    minimum = min(current, achieved)
    maximum = max(current, achieved)
    span = max(abs(maximum - minimum), 1e-6)
    ax.set_xlim(minimum - 0.15 * span, maximum + 0.15 * span)
    ax.set_ylim(-0.8, 0.8)
    ax.axhline(0, linewidth=2)
    ax.scatter([current], [0], s=120, zorder=5)
    ax.scatter([achieved], [0], s=120, zorder=5)
    ax.annotate(
        f"Current\n{current:.4f}", xy=(current, 0), xytext=(current, 0.45),
        ha="center", arrowprops=dict(arrowstyle="->"),
    )
    ax.annotate(
        f"After change\n{achieved:.4f}", xy=(achieved, 0),
        xytext=(achieved, -0.50), ha="center",
        arrowprops=dict(arrowstyle="->"),
    )
    ax.annotate(
        "", xy=(achieved, 0), xytext=(current, 0),
        arrowprops=dict(arrowstyle="<->", linewidth=2),
    )
    ax.text(
        (current + achieved) / 2, 0.13, f"Change: {achieved - current:+.4f}",
        ha="center", fontsize=10, fontweight="bold",
    )
    if target is not None:
        target = float(target)
        ax.axvline(target, linestyle="--", linewidth=1.5)
        ax.text(target, 0.68, f"Target\n{target:.4f}", ha="center", fontsize=8)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_yticks([])
    ax.set_xlabel("Model output")
    plt.tight_layout()
    plt.show()
    return fig


def _value_at(values, index):
    if values is None:
        return None
    try:
        return float(values[index])
    except Exception:
        try:
            return float(np.asarray(values).reshape(-1)[index])
        except Exception:
            return None


# ================================================================
# 1. FIT DISPLAY
# ================================================================


def show_fit(model, feature_names=None, verbose=False):
    """Display model readiness, learned structure, and the learned DAG."""
    _header("CAUSE-XAI — MODEL READY")

    print("\nStatus")
    _line()
    print("  ✓ Causal structure discovered")
    print("  ✓ Causal mechanisms fitted")
    print("  ✓ Model ready for explanation")

    adj = getattr(model, "_adj", None)
    if adj is None:
        adj = getattr(model, "adj_", None)
    if adj is None:
        print("\nCausal structure information is unavailable.")
        return None

    adj = np.asarray(adj)
    p = adj.shape[0]
    names = list(feature_names) if feature_names is not None else [f"X{i + 1}" for i in range(p)]

    edges = [(i, j) for i in range(p) for j in range(p) if adj[i, j] != 0]
    parents = {j: [] for j in range(p)}
    children = {i: [] for i in range(p)}
    for i, j in edges:
        children[i].append(j)
        parents[j].append(i)

    roots = [names[i] for i in range(p) if not parents[i]]
    sinks = [names[i] for i in range(p) if not children[i]]

    print("\nCausal structure")
    _line()
    print(f"  Variables                : {p}")
    print(f"  Relationships discovered : {len(edges)}")
    print(f"  Root variables           : {len(roots)}")
    print(f"  Sink variables           : {len(sinks)}")

    if roots:
        print(f"  Roots                    : {', '.join(roots)}")

    print("\nDAG")
    _line()
    print("  Root variables are highlighted in the graph.")

    try:
        dag = show_dag(model, feature_names=names)
        if dag is not None:
            try:
                from IPython.display import display as ipy_display
                ipy_display(dag)
            except Exception:
                try:
                    dag.view()
                except Exception:
                    print("\n  DAG object created successfully.")
        return dag
    except Exception as exc:
        print(f"\n  DAG visualization unavailable: {exc}")
        return None


# ================================================================
# 2. COUNTERFACTUAL DISPLAY
# ================================================================


def show_counterfactual(result: CCEResult, feature_names=None):
    """Display the user-facing causal counterfactual and its causal diagnostics."""
    names = _names(result.x_obs, feature_names)
    _header("COUNTERFACTUAL EXPLANATION")

    print("\nWhat would need to change?")
    _line()
    direct = result.direct_interventions or []

    if result.feasible and direct:
        for j in direct:
            old = float(result.x_obs[j])
            new = float(result.x_star[j])
            print(f"\n  {names[j]}")
            print(f"    Current value : {old:.3f}")
            print(f"    New value     : {new:.3f}")
            print(f"    Required      : {_format_change(old, new).lower()}")
    elif result.feasible and result.changed:
        for j in result.changed:
            old = float(result.x_obs[j])
            new = float(result.x_star[j])
            print(f"\n  {names[j]}")
            print(f"    Current value : {old:.3f}")
            print(f"    New value     : {new:.3f}")
            print(f"    Required      : {_format_change(old, new).lower()}")
    else:
        print("  No feasible feature change was found under the current causal constraints.")

    print("\nCausal validity")
    _line()
    if float(result.violation) < 1.5:
        print("  ✓ The resulting state is consistent with the learned causal structure.")
    else:
        print("  ⚠ The resulting state may be inconsistent with the learned causal structure.")
    print(f"\n  Causal distance : {float(result.d_causal):.3f}")
    print(f"  Causal sparsity : {float(result.sparsity):.2f}")
    print(f"  Runtime         : {float(result.runtime):.3f} sec")

    changed = result.changed or []
    downstream = [j for j in changed if j not in direct]
    total_features = len(result.x_obs)
    violation = float(result.violation)

    metrics = [
        {
            "title": "DIRECT INTERVENTIONS",
            "value": f"{len(direct)} / {total_features}",
            "explanation": "Features intentionally changed\nto obtain the counterfactual.",
        },
        {
            "title": "DOWNSTREAM CHANGES",
            "value": str(len(downstream)),
            "explanation": "Additional features that changed\nbecause of causal propagation.",
        },
        {
            "title": "CAUSAL SPARSITY",
            "value": f"{float(result.sparsity) * 100:.1f}%",
            "explanation": "How concentrated the solution is.\nHigher means fewer direct changes.",
        },
        {
            "title": "CAUSAL CONSISTENCY",
            "value": "✓ Consistent" if violation < 1.5 else "⚠ Check",
            "explanation": f"Constraint score: {violation:.4f}\nLower indicates better consistency.",
        },
        {
            "title": "CAUSAL DISTANCE",
            "value": f"{float(result.d_causal):.4f}",
            "explanation": "Distance of the counterfactual\nfrom the observed causal state.",
        },
        {
            "title": "RUNTIME",
            "value": f"{float(result.runtime):.2f} s",
            "explanation": "Time required to find\nthe counterfactual.",
        },
    ]
    _show_metric_cards(metrics)

    print("\nDIRECT INTERVENTIONS")
    _line()
    if direct:
        rows = []
        for j in direct:
            old = float(result.x_obs[j])
            new = float(result.x_star[j])
            rows.append([
                names[j], f"{old:.4f}", f"{new:.4f}",
                f"{new - old:+.4f}", _format_change(old, new),
            ])
        _show_table(
            rows,
            ["Feature", "Current", "New value", "Change", "Required action"],
            title="Direct causal interventions",
            figsize=(12, max(3, 2 + 0.45 * len(rows))),
        )
    else:
        print("  No direct feature intervention.")

    print("\nDOWNSTREAM EFFECTS")
    _line()
    if downstream:
        print(f"  {len(downstream)} feature(s) changed as a consequence of the direct intervention.")
        rows = []
        for j in downstream:
            old = float(result.x_obs[j])
            new = float(result.x_star[j])
            rows.append([names[j], f"{old:.4f}", f"{new:.4f}", f"{new - old:+.4f}"])
        _show_table(
            rows,
            ["Feature", "Original", "Causal result", "Change"],
            title="Downstream causal changes",
            figsize=(10, max(3, 2 + 0.45 * len(rows))),
        )
    else:
        print("  No downstream feature changes.")
    print()


# ================================================================
# 3. CAUSAL FEATURE IMPACT / CAI
# ================================================================


def show_attribution(result: CAIResult, feature_names=None):
    """Display the complete CAI table, uncertainty, and main causal driver."""
    names = _names(result.x_obs, feature_names)
    cai = np.asarray(result.cai, dtype=float)
    if cai.size == 0:
        _header("CAUSAL FEATURE IMPACT")
        print("\n  No CAI values available.")
        return None

    order = np.argsort(np.abs(cai))[::-1]
    top = int(order[0])
    top_effect = float(cai[top])

    _header("CAUSAL FEATURE IMPACT")
    print(
        "\nThe causal effect estimates how intervening on each feature "
        "changes the expected model output."
    )
    if result.n_samples is not None:
        print(f"\n  Monte Carlo samples : {result.n_samples}")

    print("\nFeature-level causal effects")
    _line()
    rows = []
    for rank, j in enumerate(order):
        j = int(j)
        intervention = _value_at(result.intervention_values, j)
        if intervention is None:
            intervention = float(result.x_obs[j])
        f_do = _value_at(result.f_do, j)
        effect = float(cai[j])
        se = _value_at(result.standard_errors, j)
        ci = None
        if result.confidence_intervals is not None:
            try:
                ci = _format_ci(result.confidence_intervals[j])
            except Exception:
                ci = None
        rows.append([
            rank + 1,
            names[j],
            f"{intervention:.4f}" if intervention is not None else "-",
            f"{f_do:.4f}" if f_do is not None else "-",
            f"{effect:+.4f}",
            f"{se:.4f}" if se is not None else "-",
            ci if ci is not None else "-",
            _effect_description(effect),
        ])

    _show_table(
        rows,
        [
            "Rank", "Feature", "Intervention", "E[f | do]", "CAI",
            "SE", "95% CI", "Interpretation",
        ],
        title="Feature-level causal effects",
        figsize=(15, max(4, min(16, 1.5 + 0.40 * len(rows)))),
        font_size=8,
    )

    print("\nMain causal driver")
    _line()
    print(f"  {_direction_sentence(names[top], top_effect)}")
    print(f"  CAI : {top_effect:+.4f}")
    print(f"  Baseline expected output : {float(result.baseline):.4f}")
    print()


# ================================================================
# 4. UNIFIED EXPLANATION
# ================================================================


def show_explanation(explanation: UnifiedExplanation, feature_names=None):
    """Display the complete high-level CAUSE-XAI explanation."""
    names = _names(explanation.x_obs, feature_names)
    cce = explanation.cce
    cai = explanation.cai
    cai_values = np.asarray(cai.cai, dtype=float)

    if cai_values.size == 0:
        _header("CAUSE-XAI — MODEL EXPLANATION")
        print("\n  No causal attribution values available.")
        return

    order = np.argsort(np.abs(cai_values))[::-1]
    top = int(order[0])
    top_effect = float(cai_values[top])
    direct = cce.direct_interventions or []
    changed = cce.changed or []
    downstream = [j for j in changed if j not in direct]

    _header("CAUSE-XAI — MODEL EXPLANATION")

    print("\n1. Prediction")
    _line()
    print(f"  Current output : {float(explanation.y_fact):.4f}")
    print(f"  Target output  : {float(explanation.y_foil):.4f}")
    print(f"  Achieved output: {float(cce.y_achieved):.4f}")
    if cce.feasible:
        print("\n  ✓ A feasible causal counterfactual was found.")
    else:
        print("\n  ✗ The requested target could not be reached.")

    print("\n2. Top causal factors")
    _line()
    rows = []
    for rank, j in enumerate(order[:min(5, len(order))]):
        j = int(j)
        effect = float(cai_values[j])
        rows.append([
            rank + 1,
            names[j],
            f"{effect:+.4f}",
            _effect_description(effect),
        ])
    _show_table(
        rows,
        ["Rank", "Feature", "CAI", "Interpretation"],
        title="Top causal factors",
        figsize=(10, max(3.5, 1.8 + 0.55 * len(rows))),
    )

    print("\n3. What would need to change?")
    _line()
    if direct:
        rows = []
        for j in direct:
            old = float(cce.x_obs[j])
            new = float(cce.x_star[j])
            rows.append([
                "★", names[j], f"{old:.4f}", f"{new:.4f}",
                f"{new - old:+.4f}", _format_change(old, new),
            ])
        _show_table(
            rows,
            ["", "Feature", "Current", "Required", "Δ", "Action"],
            title="Direct causal actions",
            figsize=(11, max(3, 2 + 0.5 * len(rows))),
        )
    else:
        print("  No direct causal intervention was identified.")

    print("\n4. Causal validity")
    _line()
    if float(cce.violation) < 1.5:
        print("  ✓ The counterfactual remains consistent with the learned causal structure.")
    else:
        print("  ⚠ The counterfactual may violate the learned causal structure.")
    print(f"  Causal distance : {float(cce.d_causal):.4f}")
    print(f"  Causal sparsity : {float(cce.sparsity):.2f}")
    print(f"  Runtime         : {float(cce.runtime):.3f} sec")

    if downstream:
        print("\n5. Causal propagation")
        _line()
        print(f"  {len(downstream)} feature(s) changed as a consequence of the direct intervention.")
        print("  These are consequences of the causal structure, not additional user actions.")
        rows = []
        for j in downstream:
            old = float(cce.x_obs[j])
            new = float(cce.x_star[j])
            rows.append([names[j], f"{old:.4f}", f"{new:.4f}", f"{new - old:+.4f}"])
        _show_table(
            rows,
            ["Feature", "Original", "After propagation", "Change"],
            title="Downstream causal effects",
            figsize=(10, max(3, 2 + 0.45 * len(rows))),
        )
    else:
        print("\n5. Causal propagation")
        _line()
        print("  No downstream causal changes.")

    print("\n6. Causal quality")
    _line()
    metrics = [
        {
            "title": "DIRECT CHANGES",
            "value": f"{len(direct)} / {len(explanation.x_obs)}",
            "explanation": "Features deliberately changed\nto obtain the target.",
        },
        {
            "title": "DOWNSTREAM EFFECTS",
            "value": str(len(downstream)),
            "explanation": "Features that changed because\nof causal propagation.",
        },
        {
            "title": "CAUSAL SPARSITY",
            "value": f"{float(cce.sparsity) * 100:.1f}%",
            "explanation": "Higher means fewer direct changes.",
        },
        {
            "title": "CAUSAL CONSISTENCY",
            "value": "✓ Consistent" if float(cce.violation) < 1.5 else "⚠ Check",
            "explanation": f"Constraint score: {float(cce.violation):.4f}",
        },
        {
            "title": "CAUSAL DISTANCE",
            "value": f"{float(cce.d_causal):.4f}",
            "explanation": "Distance from observed causal state.",
        },
        {
            "title": "RUNTIME",
            "value": f"{float(cce.runtime):.2f} s",
            "explanation": "Time required to compute the explanation.",
        },
    ]
    _show_metric_cards(metrics)

    print("\n7. Conclusion")
    _line()
    print(f"  {_direction_sentence(names[top], top_effect)}")
    if cce.feasible:
        print(
            f"\n  A causal intervention changes the model output from "
            f"{float(cce.y_fact):.4f} to {float(cce.y_achieved):.4f}."
        )
    else:
        print(
            f"\n  The requested target {float(cce.y_foil):.4f} could not be reached "
            "under the learned causal constraints."
        )
    print()


# ================================================================
# 5. CAI VS SHAP
# ================================================================


def show_cai_vs_shap(comparison: dict, feature_names=None):
    """Display CAI vs SHAP-style interpretation, plots, and comparison table."""
    if not isinstance(comparison, dict):
        raise TypeError("comparison must be a dictionary.")

    required = {"cai", "shap_style", "baseline_int", "baseline_obs"}
    missing = [key for key in required if key not in comparison]
    if missing:
        raise KeyError("CAI vs SHAP comparison is missing: " + ", ".join(missing))

    cai = np.asarray(comparison["cai"], dtype=float)
    shap = np.asarray(comparison["shap_style"], dtype=float)
    if cai.shape != shap.shape:
        raise ValueError("CAI and SHAP arrays must have the same shape.")

    names = _names(cai, feature_names)
    difference = cai - shap
    order = np.argsort(np.abs(difference))[::-1]
    bias_threshold = 0.05

    _header("CAUSAL vs OBSERVATIONAL ATTRIBUTION")

    print("\nCAI")
    _line()
    print("  Measures the change in expected model output under an active feature intervention.")

    print("\nSHAP-style")
    _line()
    print("  Describes feature contribution using observational relationships.")

    print("\nWhy compare them?")
    _line()
    print(
        "  Large disagreement means that the feature's observational contribution "
        "differs from its estimated interventional effect."
    )

    print("\nREFERENCE OUTPUTS")
    _line()
    print(f"  Interventional baseline : {float(comparison['baseline_int']):.4f}")
    print(f"  Observational baseline  : {float(comparison['baseline_obs']):.4f}")

    plt = _get_plt()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(shap, cai, s=42)
    minimum = min(float(np.min(shap)), float(np.min(cai)))
    maximum = max(float(np.max(shap)), float(np.max(cai)))
    padding = (maximum - minimum) * 0.08 + 1e-6
    ax.plot(
        [minimum - padding, maximum + padding],
        [minimum - padding, maximum + padding],
        linestyle="--", linewidth=1.5,
    )
    for i in range(len(names)):
        ax.annotate(
            names[i], (shap[i], cai[i]), fontsize=7,
            xytext=(4, 4), textcoords="offset points",
        )
    ax.set_xlabel("SHAP-style attribution")
    ax.set_ylabel("CAI")
    ax.set_title("CAI vs SHAP-style attribution", fontweight="bold")
    ax.grid(alpha=0.2)
    plt.tight_layout()
    plt.show()

    sorted_names = [names[int(j)] for j in order]
    sorted_difference = [float(difference[int(j)]) for j in order]
    fig, ax = plt.subplots(figsize=(10, max(5, 0.35 * len(order))))
    y = np.arange(len(order))
    ax.barh(y, sorted_difference)
    ax.axvline(0, linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels(sorted_names)
    ax.invert_yaxis()
    ax.set_xlabel("CAI − SHAP-style")
    ax.set_title("Where CAI and SHAP-style attribution disagree", fontweight="bold")
    plt.tight_layout()
    plt.show()

    print("\nDETAILED COMPARISON")
    _line()
    rows = []
    n_biased = 0
    for rank, j in enumerate(order):
        j = int(j)
        diff = float(difference[j])
        biased = abs(diff) > bias_threshold
        if biased:
            n_biased += 1
        rows.append([
            rank + 1,
            names[j],
            f"{cai[j]:+.4f}",
            f"{shap[j]:+.4f}",
            f"{diff:+.4f}",
            "⚠" if biased else "✓",
        ])

    _show_table(
        rows,
        ["Rank", "Feature", "CAI", "SHAP", "Difference", "Flag"],
        title="CAI vs SHAP-style comparison",
        figsize=(11, max(4, min(15, 1.5 + 0.35 * len(rows)))),
        font_size=8,
    )

    print(f"\n  Features with |CAI − SHAP| > {bias_threshold:.2f}: {n_biased}/{len(cai)}")
    if len(order):
        largest = int(order[0])
        print("\nLARGEST DISAGREEMENT")
        _line()
        print(f"  Feature    : {names[largest]}")
        print(f"  CAI        : {cai[largest]:+.4f}")
        print(f"  SHAP       : {shap[largest]:+.4f}")
        print(f"  Difference : {difference[largest]:+.4f}")
    print()


# ================================================================
# 6. DAG DISPLAY
# ================================================================


def show_dag(model, feature_names=None):
    """Create a Graphviz representation of the learned DAG with roots highlighted."""
    try:
        from graphviz import Digraph
    except ImportError as exc:
        raise ImportError(
            "DAG visualization requires the Python graphviz package.\n"
            "Install with:\n"
            "    pip install graphviz"
        ) from exc

    adj = np.asarray(model._adj)
    p = adj.shape[0]
    names = list(feature_names) if feature_names is not None else [f"X{i + 1}" for i in range(p)]

    dot = Digraph("CAUSE_XAI_DAG")
    dot.attr(
        rankdir="LR",
        splines="ortho",
        nodesep="0.30",
        ranksep="0.55",
        bgcolor="white",
    )
    dot.attr(
        "node",
        shape="box",
        style="rounded",
        fontsize="9",
        margin="0.08",
    )
    dot.attr("edge", arrowsize="0.55", penwidth="0.9")

    for i, name in enumerate(names):
        has_parent = bool(np.any(adj[:, i]))
        has_child = bool(np.any(adj[i, :]))
        is_root = not has_parent
        is_sink = not has_child

        if is_root:
            label = f"{name}\\n(ROOT)"
            dot.node(
                str(i), label,
                style="rounded,filled",
                fillcolor="lightyellow",
                penwidth="2.0",
            )
        elif is_sink:
            label = f"{name}\\n(sink)"
            dot.node(str(i), label)
        else:
            dot.node(str(i), name)

    for i in range(p):
        for j in range(p):
            if adj[i, j] != 0:
                dot.edge(str(i), str(j))

    return dot


# ================================================================
# 7. GENERIC DISPLAY
# ================================================================


def display(result, feature_names=None):
    """Automatically select the appropriate CAUSE-XAI display."""
    if isinstance(result, UnifiedExplanation):
        return show_explanation(result, feature_names=feature_names)
    if isinstance(result, CCEResult):
        return show_counterfactual(result, feature_names=feature_names)
    if isinstance(result, CAIResult):
        return show_attribution(result, feature_names=feature_names)
    if isinstance(result, dict):
        if "cai" in result and "shap_style" in result:
            return show_cai_vs_shap(result, feature_names=feature_names)
        raise TypeError("Dictionary does not contain a recognised CAUSE-XAI result.")
    raise TypeError(f"Unsupported result type: {type(result).__name__}")


__all__ = [
    "show_fit",
    "show_counterfactual",
    "show_attribution",
    "show_explanation",
    "show_cai_vs_shap",
    "show_dag",
    "display",
]
