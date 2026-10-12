"""Oracle keep-best over a JSONL of reveal judgments.

Each line is one candidate::

    {"prompt_id": "MIST-...", "stage": "reveal", "pass": 0, "score": 0.2,
     "checks": {"reveal_attempt_visible": 0, "memory_state_matches_expected": 0}}

``pass`` is generation order. Ties keep the earlier pass. A baseline file
has one row per id. ``--with-baseline`` leaves that clip eligible.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .bootstrap import paired_delta_ci
from .keep import Candidate, keep_best


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    if not rows:
        raise ValueError(f"no rows in {path}")
    return rows


def _index(row: dict, order: int) -> int:
    if "pass" in row:
        return int(row["pass"])
    if "index" in row:
        return int(row["index"])
    return order


def _flag(row: dict, key: str) -> bool | None:
    checks = row.get("checks") or {}
    if key not in checks or checks[key] is None:
        return None
    return float(checks[key]) >= 0.5


def _group(rows: list[dict], stage: str) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        if str(row.get("stage", "reveal")) != stage:
            continue
        grouped.setdefault(str(row["prompt_id"]), []).append(row)
    if not grouped:
        raise ValueError(f"no rows for stage {stage}")
    for group in grouped.values():
        group.sort(key=lambda row: _index(row, 0))
    return grouped


def _select(group: list[dict]) -> tuple[Candidate, dict]:
    candidates = []
    by_index: dict[int, dict] = {}
    for order, row in enumerate(group):
        index = _index(row, order)
        seed = row.get("seed")
        candidates.append(
            Candidate(
                case_id=str(row["prompt_id"]),
                source=str(row.get("source") or "pass"),
                index=index,
                prompt=str(row.get("prompt") or ""),
                score=float(row["score"]),
                seed=None if seed is None else int(seed),
            )
        )
        by_index[index] = row
    best = keep_best(candidates)
    return best, by_index[best.index]


def _rate(flags: list[bool | None]) -> float | None:
    present = [flag for flag in flags if flag is not None]
    if not present:
        return None
    return sum(1 for flag in present if flag) / len(present)


def summarize(
    judgments: list[dict],
    baseline: list[dict] | None = None,
    *,
    stage: str = "reveal",
    with_baseline: bool = False,
) -> dict:
    grouped = _group(judgments, stage)
    base_group = _group(baseline, stage) if baseline is not None else {}
    if with_baseline and baseline is None:
        raise ValueError("with_baseline requires a baseline file")

    per_id = []
    open_flags: list[bool | None] = []
    inside_flags: list[bool | None] = []
    base_scores: list[float] = []
    paired_ids: list[str] = []

    for case_id in sorted(grouped):
        best, row = _select(grouped[case_id])
        arm_score = best.score
        kept = best
        if with_baseline:
            if case_id not in base_group:
                raise ValueError(f"{case_id} is missing from the baseline")
            base_best, _base_row = _select(base_group[case_id])
            original = Candidate(
                case_id=case_id,
                source="original",
                index=-1,
                prompt=base_best.prompt,
                score=base_best.score,
                seed=base_best.seed,
            )
            kept = keep_best([original, best])
        record = {
            "id": case_id,
            "kept_source": kept.source,
            "kept_pass": kept.index,
            "kept_score": kept.score,
            "arm_pass": best.index,
            "arm_score": arm_score,
        }
        if case_id in base_group:
            base_score = _select(base_group[case_id])[0].score
            record["baseline_score"] = base_score
            base_scores.append(base_score)
            paired_ids.append(case_id)
        chosen_row = row if kept.source != "original" else _select(base_group[case_id])[1]
        open_flags.append(_flag(chosen_row, "reveal_attempt_visible"))
        inside_flags.append(_flag(chosen_row, "memory_state_matches_expected"))
        per_id.append(record)

    report = {
        "n": len(per_id),
        "stage": stage,
        "with_baseline": with_baseline,
        "kept_reveal_mean": sum(item["kept_score"] for item in per_id) / len(per_id),
        "arm_reveal_mean": sum(item["arm_score"] for item in per_id) / len(per_id),
        "kept_open_rate": _rate(open_flags),
        "kept_inside_rate": _rate(inside_flags),
        "per_id": per_id,
    }
    if paired_ids:
        lo, hi = paired_delta_ci(
            [item["kept_score"] for item in per_id if item["id"] in paired_ids],
            [item["baseline_score"] for item in per_id if item["id"] in paired_ids],
        )
        report["paired_delta_ci95"] = [lo, hi]
        report["baseline_reveal_mean"] = sum(base_scores) / len(base_scores)
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Oracle keep-best over reveal judgments.")
    parser.add_argument("--judgments", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, default=None)
    parser.add_argument(
        "--with-baseline",
        action="store_true",
        help="Leave the baseline clip eligible. A worse rewrite is not kept.",
    )
    parser.add_argument("--stage", default="reveal")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    baseline = load_jsonl(args.baseline) if args.baseline else None
    report = summarize(
        load_jsonl(args.judgments),
        baseline,
        stage=args.stage,
        with_baseline=args.with_baseline,
    )
    text = json.dumps(report, indent=2)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
