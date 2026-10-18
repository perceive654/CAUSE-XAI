
# TARGET_PROB = 0.55


# EPS_TOL = 1.5


# DEFAULTS = {
#     "lambda_": 0.5,       # causal distance weight
#     "mu": 40.0,           # unused in current search, kept for API
#     "K_cce": 30,          # MC samples for counterfactual prediction
#     "K_cai": 150,         # MC samples for CAI
#     "n_restarts": 3,      # unused in current search, kept for API
#     "top_k": 10,          # max number of candidate intervention features
# }

"""Configuration defaults matching the verified CCE-ANM notebook."""

TARGET_PROB = 0.55
EPS_TOL = 1.5

DEFAULTS = {
    "lambda_": 2.0,
    "mu": 50.0,
    "K_cce": 30,
    "K_cai": 1000,
    "top_k": 10,
    "target_prob": 0.55,
    "search_feasibility": "instance",
    "random_state": 42,
    "percentile": 75.0,
    "cycle_strategy": "weakest",
}
