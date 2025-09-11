#!/usr/bin/env python3
"""
Entry point that boots the existing UI_Manager UI.
"""

import importlib
import sys

def _opt_attr(mod, *names):
    for n in names:
        f = getattr(mod, n, None)
        if callable(f):
            return f
    return None

def main():
    try:
        ui = importlib.import_module("UI_Manager")
    except Exception as e:
        print("Failed to import UI_Manager:", e, file=sys.stderr)
        sys.exit(1)

    # Prefer an existing entry-point if you already have one.
    entry = _opt_attr(ui, "main", "run", "start", "launch")
    if entry:
        return entry()

    # Otherwise, call our unified bootstrap (we’ll add it below in UI_Manager.py)
    if hasattr(ui, "launch_unified_ui"):
        return ui.launch_unified_ui()

    print("UI_Manager has no main()/run()/start()/launch() or launch_unified_ui().", file=sys.stderr)
    sys.exit(2)

if __name__ == "__main__":
    main()
