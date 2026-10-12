#!/usr/bin/env python3
"""Synthetic dry run. Does not call Wan or a judge."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from videomist.dry import main

if __name__ == "__main__":
    main()
