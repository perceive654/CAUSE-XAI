# tests/conftest.py

import numpy as np
import pytest

from cause.anm import ANM


@pytest.fixture
def chain_anm():
    """
    Simple chain ANM: X1 → X2 → X3
    """
    adj = np.array(
        [
            [0, 1, 0],
            [0, 0, 1],
            [0, 0, 0],
        ]
    )
    order = [0, 1, 2]
    return adj, order