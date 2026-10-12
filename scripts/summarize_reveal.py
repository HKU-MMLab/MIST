#!/usr/bin/env python3
"""Oracle keep-best over a JSONL of reveal judgments."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from videomist.summarize import main

if __name__ == "__main__":
    main()
