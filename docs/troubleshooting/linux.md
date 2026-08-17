# Linux

Generally the smoothest platform for this. A few distro-specific notes.

## venv module missing

Debian and Ubuntu split it into a separate package:

```bash
sudo apt install python3-venv python3-pip
```

Fedora:
```bash
sudo dnf install python3-pip
```

Arch has it in the base Python package already.

## "externally-managed-environment"

Recent distros protect the system Python. Use a venv; that is the intended
answer:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Do not reach for `--break-system-packages`.

## Python too old

Moonfield needs 3.10+ (for `zoneinfo` and modern typing). Check:

```bash
python3 --version
```

On older LTS releases, use your distro's newer Python package
(`python3.11`, `python3.12`) or `pyenv`.

## Timezone database

Almost always present. If `zoneinfo` complains:

```bash
sudo apt install tzdata        # Debian/Ubuntu
pip install tzdata             # or, inside the venv
```

## Config location

Follows the XDG spec:

```
$XDG_CONFIG_HOME/moonfield/config.json
```

falling back to `~/.config/moonfield/config.json`.

```bash
moonfield config path
```

You can override it entirely with the `MOONFIELD_CONFIG` environment variable,
useful if you want separate configs for different observing sites.

## Headless / server

Everything works without a display. The ASCII Moon needs only a UTF-8 locale:

```bash
echo $LANG        # want something ending in .UTF-8
```

If not, `--no-art` works everywhere.

## See also

- [Getting unstuck](getting-unstuck.md) · [Environment reset](environment-reset.md)
