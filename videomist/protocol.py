"""Protocol constants named by the paper and the surviving launch scripts.

``MIST_SEED_CLASS`` is the baseline seed class in the appendix. The sampler
that turned that class into Wan noise was deleted with the experiment tree
and is not reimplemented here. The 2026-09-19 no-gold passes used
``e6_seed`` instead.
"""

from __future__ import annotations

REVEAL_POSITIONS = (0.90, 0.93, 0.95, 0.97, 0.99, 0.995)
MIST_SEED_CLASS = 9042
K = 5
SHOTS = 3
SHOT_SECONDS = 5
BOOTSTRAP_RESAMPLES = 4000
BOOTSTRAP_SEED = 0
GENERATOR = "Wan2.2-TI2V-5B"
OFFICIAL_GENERATOR = "Wan2.2-T2V-A14B"
JUDGE = "Qwen3.5-122B-A10B"
BLIND_SELECTOR = "Qwen3-VL-8B-Instruct"
WAN_STEPS = 50
WAN_SIZE = "1280*704"
OFFICIAL_SECONDS = 10
OFFICIAL_FRAMES = 161


def e6_seed(k: int) -> int:
    """Seed for no-gold pass ``k``: ``1000 + k * 137``."""
    if k < 0:
        raise ValueError(k)
    return 1000 + k * 137


def as_dict() -> dict:
    return {
        "generator": GENERATOR,
        "official_generator": OFFICIAL_GENERATOR,
        "judge": JUDGE,
        "blind_selector": BLIND_SELECTOR,
        "shots": SHOTS,
        "shot_seconds": SHOT_SECONDS,
        "k": K,
        "seed_class": MIST_SEED_CLASS,
        "seed_class_note": (
            "Named in the paper. The original sampler was deleted and is not reimplemented."
        ),
        "e6_seed": "1000 + k * 137",
        "e6_seeds": [e6_seed(k) for k in range(K)],
        "reveal_positions": list(REVEAL_POSITIONS),
        "wan_steps": WAN_STEPS,
        "wan_size": WAN_SIZE,
        "official_seconds": OFFICIAL_SECONDS,
        "official_frames": OFFICIAL_FRAMES,
        "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
        "bootstrap_seed": BOOTSTRAP_SEED,
    }
