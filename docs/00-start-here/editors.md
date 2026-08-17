# Editors and IDEs

**This lesson is optional.** You can complete the entire curriculum with a
terminal and nothing else. Read this if you are curious, or if you want to start
changing the code.

---

## What is an editor? What is an IDE?

An **editor** is a program for writing text files. Code is text files. Word
processors are not suitable — they add invisible formatting that breaks code.

An **IDE** (Integrated Development Environment) is an editor plus extra tools:
running code, debugging, autocomplete, jumping to a function's definition.

The distinction is fuzzy and does not matter much. Both let you edit files.

## Do I need one?

No. Moonfield is designed terminal-first, and every lesson works that way.

An editor helps when you want to:

- Read several source files while following a lesson
- Change a value and immediately see what breaks
- Search the whole project for a term
- Write your own scripts

## The options

### Terminal editors

Already installed, no setup, work over SSH.

- **nano** — the friendly one. Commands are listed at the bottom. `Ctrl+O` to
  save, `Ctrl+X` to exit. If you have never used a terminal editor, start here.
- **vim** — powerful, and famously hard to *exit*. (It is `:q!`.) Worth learning
  eventually, not today.
- **micro** — modern feel, familiar shortcuts. Needs installing.

```bash
nano src/moonfield/phase.py
```

### Graphical editors

- **VS Code** — free, popular, excellent Python support. The usual first choice.
- **VSCodium** — VS Code without Microsoft's telemetry.
- **PyCharm Community** — free, Python-specific, heavier but very capable.
- **Cursor**, **Zed**, **Sublime Text** — all fine.

Whatever you already know is the right answer. Nothing here requires a
particular one.

---

## The one thing that actually matters: the interpreter

This is the concept that causes almost all IDE confusion, so it is worth a
minute.

Your computer may have several Pythons: a system one, one from python.org, one
from the app store, and one inside each project's virtual environment.

When you activate `.venv` in a terminal, you tell *that terminal* to use *that*
Python. But your editor is a separate program. It does not know what your
terminal did. Unless you tell it, it may use a completely different Python —
one where Moonfield is not installed.

That produces the classic confusing symptom:

> It runs fine in my terminal but my editor says `ModuleNotFoundError: No module
> named 'moonfield'`.

Nothing is broken. The editor is just looking in the wrong place.

### Fixing it in VS Code

1. Open the `moonfield` folder (File → Open Folder)
2. `Ctrl+Shift+P` (`Cmd+Shift+P` on macOS)
3. Type "Python: Select Interpreter"
4. Choose the one with `.venv` in its path — usually marked "Recommended"

The chosen interpreter shows in the bottom status bar. If it does not say
`.venv`, that is your problem.

### Fixing it in PyCharm

Settings → Project → Python Interpreter → gear icon → Add → Existing
Environment → point at `moonfield/.venv/bin/python` (or
`.venv\Scripts\python.exe` on Windows).

### Checking from anywhere

```python
import sys
print(sys.executable)
```

If that path does not contain `.venv`, your editor is on the wrong interpreter.

---

## A minimal setup

If you want VS Code configured for this project and nothing more:

1. Install VS Code
2. Install the **Python** extension by Microsoft
3. Open the `moonfield` folder
4. Select the `.venv` interpreter as above
5. Open a terminal inside VS Code (`Ctrl+` `` ` ``) — it usually activates the
   venv automatically

That is all. Skip the rest of the extension marketplace for now.

---

## Checkpoint

- [ ] I know what an editor and an IDE are
- [ ] I know I do not need either for this curriculum
- [ ] I understand why the Python interpreter setting matters
- [ ] If I use an editor, I have pointed it at my `.venv`
- [ ] I know how to check which Python is running

## Try it yourself

1. Open `src/moonfield/phase.py` in any editor and find `REFERENCE_NEW_MOON`
2. Change it by one day, run `moonfield phase`, see what happens
3. Change it back
4. Print `sys.executable` from both your terminal and your editor and compare

## Getting stuck?

[Getting Unstuck](../troubleshooting/getting-unstuck.md)

Next: [Module 01 — Time and place](../01-time-and-place/).
