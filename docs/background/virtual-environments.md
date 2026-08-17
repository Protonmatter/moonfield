# Virtual environments

**What they are, why every tutorial insists on them, and what actually goes
wrong without one.**

## The problem they solve

Python installs packages into a shared folder. Install two projects that need
different versions of the same library, and one of them breaks. There is no
version of this that ends well.

Worse: your operating system uses Python for its own tools. On some Linux
distributions, `sudo pip install` can genuinely break parts of your system.

## What a venv is

A folder containing its own Python interpreter and its own package directory.
Activating it changes which `python` and `pip` your shell finds.

That is all. It is not a container or a virtual machine. It is a directory and
a modified `PATH`.

```
.venv/
├── bin/           (Scripts/ on Windows)
│   ├── python
│   ├── pip
│   └── moonfield
└── lib/
    └── python3.12/site-packages/
```

## Using one

```bash
python3 -m venv .venv          # create
source .venv/bin/activate      # activate (macOS/Linux)
.\.venv\Scripts\Activate.ps1   # activate (Windows PowerShell)
deactivate                     # leave
```

Your prompt shows `(.venv)` when active. If it does not, it is not active, and
that explains most "command not found" reports.

## Things worth knowing

**It is per-project.** One venv per project directory. `.venv` is the
conventional name and is already in `.gitignore`.

**It is disposable.** Delete `.venv` and recreate it any time. Nothing of value
lives there, see [environment reset](../troubleshooting/environment-reset.md).

**Never commit it.** It contains platform-specific binaries and is often
hundreds of megabytes.

**New terminal, new activation.** Activation lasts for one shell session.

## Why Moonfield still asks for one

Moonfield has *no runtime dependencies*, so strictly you could install it
globally without conflict. We ask for a venv anyway because:

1. You will want `pytest` and `ruff` for the dev extras
2. It keeps `moonfield` off your global PATH where you might forget about it
3. It is the habit that will save you on your next project

## See also

- [Editable installs](editable-installs.md)
- [Setup](../00-start-here/setup.md)
