#!/usr/bin/env python3
"""Nexus Terminal - command entry point (nt).

This wrapper runs the main program (Nexus Terminal.py) via runpy.
Using .py file association instead of a .cmd batch file avoids the
Windows "Terminate batch job (Y/N)?" prompt that appears when pressing
Ctrl+C during batch file execution.
"""
import sys
import os
import runpy

_dir = os.path.dirname(os.path.abspath(__file__))
_main = os.path.join(_dir, 'Nexus Terminal.py')

if not os.path.isfile(_main):
    print(f'Error: Nexus Terminal.py not found in {_dir}', file=sys.stderr)
    sys.exit(1)

sys.path.insert(0, _dir)
runpy.run_path(_main, run_name='__main__')
