"""Dry run of rewrite, the leak gate, and oracle keep-best. No model calls."""

from __future__ import annotations

import argparse
import json

from examples.toy_cards import TOY_SPEC

from .cards import cards_from_obj
from .keep import Candidate
from .loop import keep_original_eligible, last_shot_prompts, score_arm
from .protocol import REVEAL_POSITIONS
from .rewrite import leaking_phrases

# Scripted reveal scores. ``original`` is the untouched clip; ``rewrites`` are the K passes.
SYNTHETIC = {
    "MIST-GAIN60-R0-03": {
        "failure": "wrong_binding",
        "nogold_failure": "hand_no_open",
        "occluder": "lid",
        "original": 0.20,
        "rewrites": [0.10, 0.55, 0.40, 0.55, 0.30],
    },
    "MIST-GAIN60-R0-02": {
        "failure": "no_action",
        "nogold_failure": "no_hand",
        "occluder": "cup",
        "original": 0.80,
        "rewrites": [0.10, 0.25, 0.40, 0.15, 0.35],
    },
}


def run_dry() -> dict:
    cards = {card.id: card for card in cards_from_obj(TOY_SPEC)}
    report = []
    for case_id, spec in SYNTHETIC.items():
        card = cards[case_id]
        gold = last_shot_prompts(card, spec["failure"], allow_gold=True)
        plain = last_shot_prompts(
            card,
            spec["nogold_failure"],
            allow_gold=False,
            occluder=spec["occluder"],
        )
        leaks = leaking_phrases(plain[0], card)
        if leaks:
            raise RuntimeError(f"{case_id} no-gold prompt still leaks: {leaks}")
        winner = score_arm(card, plain, spec["rewrites"])
        original = Candidate(
            case_id=case_id,
            source="original",
            index=-1,
            prompt=card.operation,
            score=spec["original"],
            seed=None,
        )
        kept = keep_original_eligible(original, [winner])
        report.append(
            {
                "id": case_id,
                "gold_names_target": card.expected_reveal.split(";")[0] in gold[0],
                "nogold_leak_phrases": leaks,
                "arm_best_index": winner.index,
                "arm_best_seed": winner.seed,
                "arm_best_score": winner.score,
                "kept_source": kept.source,
                "kept_score": kept.score,
            }
        )
    return {
        "kind": "synthetic_dry_run",
        "reveal_positions": list(REVEAL_POSITIONS),
        "cases": report,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Synthetic dry run of the M3-Agent control loop.")
    parser.parse_args(argv)
    print(json.dumps(run_dry(), indent=2))


if __name__ == "__main__":
    main()
