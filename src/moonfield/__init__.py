"""Moonfield -- learn the sky by running code you fully understand.

Mission
    Moonfield teaches the sky by running code you fully understand.

Method
    Observe -> predict -> learn -> run -> change -> observe -> validate -> explain.

Everything in this package is written to be read. Where a formula comes from a
textbook, the docstring says which one and what its accuracy is. Where we have
simplified, the docstring says what we dropped. If you find a comment that
explains *what* the code does but not *why*, that is a bug -- please open an
issue.

Quick start
-----------
::

    from moonfield import phase
    info = phase.compute()
    print(info.name, f"{info.illumination_percent:.0f}% lit")
"""

from __future__ import annotations

__version__ = "0.1.0"
__all__ = [
    "__version__",
    "location",
    "moon",
    "observer",
    "phase",
    "sun",
    "tides",
    "time",
]
