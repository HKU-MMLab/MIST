"""Case cards.

Accepts the small ``cases`` list used by the examples, and the deleted
spec shape ``categories[].prompts[]``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


def _phrases(value) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        text = value.strip()
        return (text,) if text else ()
    out = []
    for item in value:
        text = str(item).strip()
        if text:
            out.append(text)
    return tuple(out)


@dataclass(frozen=True)
class CaseCard:
    id: str
    setup: str
    operation: str
    expected_reveal: str
    expected_present: tuple[str, ...] = ()
    expected_absent: tuple[str, ...] = ()
    expected_count_keys: tuple[str, ...] = ()
    container: str = "container"

    def banned_phrases(self) -> list[str]:
        raw = (
            *self.expected_present,
            *self.expected_absent,
            *self.expected_count_keys,
        )
        phrases = {str(item).strip().lower() for item in raw if str(item).strip()}
        return sorted(phrases, key=len, reverse=True)


def card_from_mapping(row: dict) -> CaseCard:
    state = row.get("expected_state") or {}
    count = row.get("expected_count") or {}
    operation = row.get("operation") or row.get("final_query") or ""
    return CaseCard(
        id=str(row["id"]),
        setup=str(row.get("setup") or "").strip(),
        operation=str(operation).strip(),
        expected_reveal=str(row.get("expected_reveal") or "").strip(),
        expected_present=_phrases(row.get("expected_present")),
        expected_absent=_phrases(row.get("expected_absent")),
        expected_count_keys=_phrases(count.keys() if isinstance(count, dict) else count),
        container=str(state.get("container") or row.get("container") or "container"),
    )


def cards_from_obj(data: dict) -> list[CaseCard]:
    if "cases" in data:
        return [card_from_mapping(row) for row in data["cases"]]
    rows: list[CaseCard] = []
    for category in data.get("categories") or []:
        for prompt in category.get("prompts") or []:
            rows.append(card_from_mapping(prompt))
    if not rows:
        raise ValueError("spec has no cases")
    return rows


def load_cards(path: Path) -> list[CaseCard]:
    return cards_from_obj(json.loads(Path(path).read_text(encoding="utf-8")))
