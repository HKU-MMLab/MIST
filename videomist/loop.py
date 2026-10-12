"""Build one last-shot instruction and select among scored candidates.

Head A keeps the first two 5-second shots and resamples the last shot.
This module does not call Wan or the 122B judge.
"""

from __future__ import annotations

from .cards import CaseCard
from .keep import Candidate, keep_best
from .protocol import e6_seed
from .rewrite import revise


def last_shot_prompts(
    card: CaseCard,
    failure: str,
    *,
    allow_gold: bool,
    occluder: str = "cover",
    k: int = 5,
) -> list[str]:
    """One rewritten instruction, repeated for ``k`` seeds."""
    if k < 1:
        raise ValueError(k)
    prompt = revise(card, failure, allow_gold=allow_gold, occluder=occluder)
    return [prompt] * k


def score_arm(
    card: CaseCard,
    prompts: list[str],
    scores: list[float],
    *,
    source: str = "rewrite",
) -> Candidate:
    if len(prompts) != len(scores) or not scores:
        raise ValueError("prompts and scores must be the same non-empty length")
    candidates = [
        Candidate(
            case_id=card.id,
            source=source,
            index=i,
            prompt=prompts[i],
            score=float(scores[i]),
            seed=e6_seed(i),
        )
        for i in range(len(scores))
    ]
    return keep_best(candidates)


def keep_original_eligible(original: Candidate, rewrites: list[Candidate]) -> Candidate:
    """The original clip stays in the set. A worse rewrite is not kept."""
    return keep_best([original, *rewrites])
