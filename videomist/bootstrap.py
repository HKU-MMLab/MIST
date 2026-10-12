"""Paired bootstrap used with the reported selector comparisons.

After sorting, the percentile indexes are ``int(0.025 * n)`` and
``int(0.975 * n)``. The paper's intervals use 4,000 resamples and seed 0.
"""

from __future__ import annotations

import random
from statistics import mean

from .protocol import BOOTSTRAP_RESAMPLES, BOOTSTRAP_SEED


def paired_delta_ci(
    treatment: list[float],
    baseline: list[float],
    n: int = BOOTSTRAP_RESAMPLES,
    seed: int = BOOTSTRAP_SEED,
) -> tuple[float, float]:
    if len(treatment) != len(baseline) or not treatment:
        raise ValueError("treatment and baseline must be the same non-empty length")
    rng = random.Random(seed)
    width = len(treatment)
    diffs = []
    for _ in range(n):
        idx = [rng.randrange(width) for _ in range(width)]
        diffs.append(mean(treatment[i] - baseline[i] for i in idx))
    diffs.sort()
    return diffs[int(0.025 * n)], diffs[int(0.975 * n)]
