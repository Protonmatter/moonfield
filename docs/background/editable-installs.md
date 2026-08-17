# Editable installs

**Why `pip install -e .` and not `pip install .`**

## The difference

A normal install **copies** your code into `site-packages`. Edit the original
and nothing changes until you reinstall.

An editable install (`-e`) instead puts a **link** to your source directory.
Python reads your actual files, every time.

For a curriculum built around "change one variable and see what happens", the
second is essential. Without it, every experiment needs a reinstall, and
eventually you will edit a file, see no change, and lose twenty minutes.

## What it does

```bash
pip install -e ".[dev]"
```

- `-e` — editable
- `.` — this directory, using its `pyproject.toml`
- `[dev]` — also install the optional dev extras (pytest, ruff)

The quotes matter in zsh, which is the default shell on macOS: without them,
zsh tries to interpret the square brackets as a glob pattern.

## Checking it worked

```python
import moonfield
print(moonfield.__file__)
```

An editable install points into your project's `src/moonfield/`. A regular
install points into `site-packages`.

## The other thing it gives you

`pyproject.toml` declares:

```toml
[project.scripts]
moonfield = "moonfield.cli:main"
```

That is what creates the `moonfield` command. Without installing, you would have
to run `python -m moonfield.cli` every time. The command is a small generated
script in your venv's `bin/` that imports and calls `main()`.

## See also

- [Virtual environments](virtual-environments.md)
- [Setup](../00-start-here/setup.md)
