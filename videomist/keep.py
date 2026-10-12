"""Oracle keep-best. Ties retain the earlier candidate."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    case_id: str
    source: str
    index: int
    prompt: str
    score: float
    seed: int | None = None


def keep_best(candidates: list[Candidate]) -> Candidate:
    """Highest score wins. On a tie, the smaller index stays.

    ``index`` is generation order. Give the original clip a smaller index
    than any rewrite when both sit in the same set, so a tied rewrite is
    not kept.
    """
    if not candidates:
        raise ValueError("empty candidate set")
    best = candidates[0]
    for cand in candidates[1:]:
        if cand.score > best.score or (
            cand.score == best.score and cand.index < best.index
        ):
            best = cand
    return best
