#!/usr/bin/env python3
"""Backward-compat shim. The Dalmend Candles backlink injector has been
generalized into inject_sponsors.py. This entry point now invokes the new
script with --sponsor dalmend-candles so any old crontabs or shortcuts keep
working unchanged."""

import os, sys, runpy
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
TARGET   = BASE_DIR / "inject_sponsors.py"

if __name__ == "__main__":
    # Force the legacy script to scope itself to dalmend-candles only, unless
    # the user already passed --sponsor explicitly.
    if not any(a.startswith("--sponsor") for a in sys.argv[1:]):
        sys.argv += ["--sponsor", "dalmend-candles"]
    sys.argv[0] = str(TARGET)
    runpy.run_path(str(TARGET), run_name="__main__")
