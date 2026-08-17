# Environment reset

When something is broken in a way you cannot diagnose, starting clean is
faster than archaeology. This costs about two minutes and loses nothing except
your saved location.

## Full reset

**macOS / Linux / WSL**

```bash
cd ~/moonfield            # or wherever you cloned it
deactivate 2>/dev/null    # leave any active venv
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
moonfield doctor
```

**Windows PowerShell**

```powershell
cd $HOME\moonfield
deactivate
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
moonfield doctor
```

## Reset just the config

```bash
moonfield config clear
moonfield config path      # confirm which file it was using
```

## Undo local code changes

The lessons encourage you to edit the source. To get back to a known state:

```bash
git status                 # see what you changed
git diff                   # see exactly how
git checkout -- src/       # discard changes to source
git stash                  # or: set them aside, recoverable with 'git stash pop'
```

`git checkout --` is not undoable. Use `git stash` if there is any chance you
want the changes back.

## Nuclear option

```bash
cd ..
mv moonfield moonfield-old
git clone <your-repo-url> moonfield
cd moonfield
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Your old copy is still there in `moonfield-old` if you need anything from it.

## After any reset

```bash
moonfield doctor
python -m pytest
```

Both should be clean. If the tests fail on a fresh clone, that is a real bug.
Please [open an issue](../../issues).
