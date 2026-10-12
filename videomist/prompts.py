"""Write one last-shot instruction per case."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .cards import CaseCard, load_cards
from .protocol import K, e6_seed
from .rewrite import revise


def load_diagnoses(path: Path) -> dict[str, dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = data["diagnoses"] if isinstance(data, dict) else data
    return {str(row["id"]): row for row in rows}


def write_prompts(
    cards: list[CaseCard],
    output_dir: Path,
    *,
    failure: str | None,
    diagnoses: dict[str, dict] | None,
    allow_gold: bool,
    occluder: str,
    k: int,
) -> list[dict]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for card in cards:
        row = (diagnoses or {}).get(card.id, {})
        label = str(row.get("failure") or failure or "")
        if not label:
            raise ValueError(f"{card.id} has no failure label")
        cover = str(row.get("occluder") or occluder)
        text = revise(card, label, allow_gold=allow_gold, occluder=cover)
        (output_dir / f"{card.id}.txt").write_text(text + "\n", encoding="utf-8")
        written.append(
            {
                "id": card.id,
                "failure": label,
                "occluder": cover,
                "allow_gold": allow_gold,
                "seeds": [e6_seed(i) for i in range(k)],
                "prompt": text,
            }
        )
    return written


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Write rewritten last-shot instructions.")
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--failure", default=None, help="Label applied when a case has no diagnosis.")
    parser.add_argument("--diagnoses", type=Path, default=None)
    parser.add_argument("--allow-gold", action="store_true")
    parser.add_argument("--occluder", default="cover")
    parser.add_argument("--k", type=int, default=K)
    args = parser.parse_args(argv)
    diagnoses = load_diagnoses(args.diagnoses) if args.diagnoses else None
    rows = write_prompts(
        load_cards(args.spec),
        args.output_dir,
        failure=args.failure,
        diagnoses=diagnoses,
        allow_gold=args.allow_gold,
        occluder=args.occluder,
        k=args.k,
    )
    print(f"wrote {len(rows)} prompts to {args.output_dir}")


if __name__ == "__main__":
    main()
