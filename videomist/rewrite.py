"""Instruction rewrite.

The gold-allowed wording reconstructs the appendix rule: keep the actor,
objects, and order; replace the failed operation and the final-frame
evidence clause. It is not a byte copy of the deleted Wan prompts.

The no-gold wording is the 2026-09-19 builder. Hidden-content strings
listed on the card are banned.
"""

from __future__ import annotations

import re

from .cards import CaseCard
from .protocol import e6_seed

__all__ = [
    "E6_FAILURES",
    "E6_OCCLUDERS",
    "PAPER_FAILURES",
    "e6_seed",
    "gold_instruction",
    "leaking_phrases",
    "nogold_instruction",
    "revise",
]

PAPER_FAILURES = (
    "no_action",
    "wrong_binding",
    "missing_departure",
    "missing_return",
    "return_intact",
    "occlusion",
    "unstable_hold",
)

PAPER_OPERATIONS = {
    "no_action": "A hand must enter and complete the required operation in one continuous motion.",
    "wrong_binding": "Perform the operation on the named object only. Do not act on a neighboring object.",
    "missing_departure": "The subject must leave the frame before any return.",
    "missing_return": "After leaving, the subject must come back into the frame.",
    "return_intact": "On return, show the post-event state rather than the pre-event state.",
    "occlusion": "Move the hand and any lifted cover fully out of the frame so the result is visible.",
    "unstable_hold": "After the operation, hold the final view still until the clip ends.",
}

E6_OCCLUDERS = {"lid", "cup", "box", "board", "cover"}
E6_FAILURES = {"no_hand", "hand_no_open", "wrong_object", "already_open"}

E6_MOTION = {
    "no_hand": "A single hand must enter from one side in the first second, grasp the {occluder}, and finish one continuous opening motion.",
    "hand_no_open": "The hand is already near the {occluder}. It must grasp it and finish one full opening motion; do not stop at a touch.",
    "wrong_object": "Open only the central closed {occluder}. Do not touch a neighboring object.",
    "already_open": "Do not close anything. Clear the hand and any lifted cover fully out of the frame.",
}

E6_TAIL = (
    " Then move the hand and the removed cover entirely out of the frame. "
    "Hold the opened view still, centered, and unobstructed for the rest of the clip. "
    "Do not add, remove, recolor, or count objects. Do not print text, labels, or arrows."
)


def leaking_phrases(text: str, card: CaseCard) -> list[str]:
    low = text.lower()
    return [phrase for phrase in card.banned_phrases() if phrase and phrase in low]


def _operation_prefix(card: CaseCard) -> str:
    query = re.split(
        r"The final evidence|should match",
        card.operation,
        maxsplit=1,
        flags=re.I,
    )[0]
    return " ".join(query.split()).strip(" .")


def gold_instruction(card: CaseCard, failure: str) -> str:
    if failure not in PAPER_OPERATIONS:
        raise ValueError(f"unknown paper failure label: {failure}")
    parts = [
        "Fixed camera. Continue the same scene.",
        card.setup,
        _operation_prefix(card),
        PAPER_OPERATIONS[failure],
    ]
    if card.expected_reveal:
        parts.append("Final frame: " + card.expected_reveal)
    return " ".join(part for part in parts if part)


def nogold_instruction(card: CaseCard, occluder: str, failure: str) -> str:
    if failure not in E6_FAILURES:
        raise ValueError(f"unknown no-gold failure label: {failure}")
    if occluder not in E6_OCCLUDERS:
        occluder = "cover"
    prefix = _operation_prefix(card)
    if leaking_phrases(prefix, card):
        prefix = ""
    text = "Fixed front/top camera. Continue the same scene as the previous frame. "
    if prefix:
        text += prefix + " "
    text += E6_MOTION[failure].format(occluder=occluder) + E6_TAIL
    if leaking_phrases(text, card):
        text = (
            "Fixed front/top camera. Continue the same scene as the previous frame. "
            + E6_MOTION[failure].format(occluder="cover")
            + E6_TAIL
        )
    hit = leaking_phrases(text, card)
    if hit:
        raise ValueError(f"{card.id} still names hidden content: {hit}")
    return text


def revise(
    card: CaseCard,
    failure: str,
    *,
    allow_gold: bool,
    occluder: str = "cover",
) -> str:
    if allow_gold:
        return gold_instruction(card, failure)
    return nogold_instruction(card, occluder, failure)
