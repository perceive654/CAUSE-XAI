# src/cause/exceptions.py

class CauseXAIError(Exception):
    """Base exception for cause_xai."""
    pass


class DAGDiscoveryError(CauseXAIError):
    """Raised when DAG discovery fails or returns invalid structure."""
    pass


class ANMNotFittedError(CauseXAIError):
    """Raised when ANM methods are called before fitting."""
    pass


class CounterfactualInfeasibleError(CauseXAIError):
    """
    Raised when no feasible counterfactual is found
    within the allowed search budget.
    """
    pass


class InvalidInterventionError(CauseXAIError):
    """Raised when an intervention specification is invalid."""
    pass