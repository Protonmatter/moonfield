# macOS

## Use `python3`, not `python`

macOS ships an old Python 2 stub as `python`. Always type `python3` and `pip3`,
or work inside a venv where `python` points at the right one.

```bash
python3 --version     # needs 3.10 or newer
```

## Getting a newer Python

macOS's built-in Python is often behind. Either install from python.org, or use
Homebrew:

```bash
brew install python@3.12
```

## "command not found: moonfield"

The venv is not active. Your prompt should show `(.venv)`.

```bash
source .venv/bin/activate
```

## "externally-managed-environment" from pip

macOS is protecting its system Python. This is correct behaviour and the fix is
to use a venv, not to override it:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Do not use `--break-system-packages`. It is called that for a reason.

## Terminal.app and the Moon art

Terminal.app handles the Unicode fine in recent macOS. If it does not, use
`--no-art`, or try iTerm2.

## Location Services are not involved

Moonfield never reads your device location. You type your coordinates in once
and they are stored in a plain JSON file:

```bash
moonfield config path
```

## Apple Silicon

Everything here is pure Python — no compiled dependencies, so there are no
architecture issues. This is one of the payoffs of the zero-dependency design.

## See also

- [Getting unstuck](getting-unstuck.md) · [Environment reset](environment-reset.md)
