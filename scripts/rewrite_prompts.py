#!/usr/bin/env python3
"""Write one rewritten last-shot instruction per case."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from videomist.prompts import main

if __name__ == "__main__":
    main()
