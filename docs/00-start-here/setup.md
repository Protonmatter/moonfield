# Setup

**Goal:** a working Moonfield install, on your operating system, with you
understanding what each step did.

**Time:** 20–40 minutes the first time.

If a step fails, do not skip it. Go to
[Getting Unstuck](../troubleshooting/getting-unstuck.md) or
[open a Discussion](https://github.com/moonfield/moonfield/discussions). A
broken environment will make every later lesson confusing in ways that look
like astronomy problems but are not.

---

## What we are about to do

The same five steps on every platform:

```
clone → enter repo → create venv → activate → install → doctor → first command
```

In plain words:

1. **Clone** — copy this project from GitHub onto your computer
2. **Enter** — move your terminal into that copy
3. **Create a venv** — make a private Python workspace just for this project
4. **Activate** — tell your terminal to use that workspace
5. **Install** — put Moonfield into it
6. **Doctor** — check it all worked

---

## Step 0: open a terminal

A terminal is a window where you type commands instead of clicking. That is the
whole idea. It is not a hacker tool and there is nothing you can break by
typing the commands in this guide.

| Platform | How to open one |
|---|---|
| **Windows** | Start menu → type `PowerShell` → open **Windows PowerShell** |
| **macOS** | `Cmd + Space` → type `Terminal` → Enter |
| **Linux** | `Ctrl + Alt + T`, or search for "Terminal" |
| **Windows + WSL** | Start menu → `Ubuntu` (after installing WSL — see below) |

You will see a **prompt** — some text ending in `>` or `$` or `%`. That means
it is waiting for you. When this guide shows a command, type it and press Enter.

> **A note on WSL.** Windows Subsystem for Linux gives you a real Linux
> environment inside Windows. It is genuinely nice, and if you already have it,
> use it and follow the Linux instructions. If you do not have it, **do not
> install it just for this.** PowerShell works completely. Adding a whole
> second operating system before your first lesson is not a good trade.

---

## Step 1: check for Python

```bash
python3 --version
```

**Windows PowerShell users:** use `python --version` instead. Windows usually
does not have the `python3` name.

You want **3.10 or newer**:

```
Python 3.12.3
```

<details>
<summary><strong>"command not found" or a Microsoft Store window opened</strong></summary>

You do not have Python yet, or Windows is being unhelpful.

- **Windows:** download from [python.org/downloads](https://www.python.org/downloads/).
  During installation, **tick "Add python.exe to PATH"** on the first screen.
  This is easy to miss and causes most Windows setup problems. Then close
  PowerShell completely and open a new one.
- **macOS:** `brew install python3` if you have Homebrew, otherwise download
  from python.org.
- **Linux:** `sudo apt install python3 python3-venv python3-pip` on Debian or
  Ubuntu. On Fedora, `sudo dnf install python3 python3-pip`.

</details>

<details>
<summary><strong>It says Python 3.8 or 3.9</strong></summary>

Too old. Moonfield uses `zoneinfo`, which arrived in 3.9, and some syntax that
needs 3.10. Install a newer version from python.org. You can have several
versions installed side by side; that is normal and safe.

</details>

---

## Step 2: check for Git

```bash
git --version
```

Expected: something like `git version 2.43.0`.

<details>
<summary><strong>I do not have Git</strong></summary>

Git is a tool for downloading and tracking versions of code. Install it from
[git-scm.com/downloads](https://git-scm.com/downloads), or:

- **macOS:** `brew install git`, or just run `git --version` and let macOS
  offer to install the developer tools
- **Linux:** `sudo apt install git` or `sudo dnf install git`

**Or skip Git entirely.** Go to the GitHub page, click the green **Code**
button, choose **Download ZIP**, and unzip it. You lose the ability to pull
updates easily, but everything else works. You can install Git later.

</details>

---

## Step 3: clone the repository

```bash
git clone https://github.com/moonfield/moonfield.git
cd moonfield
```

The first line downloads a copy. The second moves your terminal *into* it. From
here on, every command assumes you are inside the `moonfield` folder.

Check you are in the right place:

```bash
ls          # Windows PowerShell: dir
```

You should see `README.md`, `pyproject.toml`, `src`, `docs`, `tests`.

<details>
<summary><strong>How do I get back here next time?</strong></summary>

`cd` means "change directory". Every new terminal starts in your home folder,
so you will need to `cd` back:

```bash
cd moonfield              # if it is in your home folder
cd ~/projects/moonfield   # if you put it somewhere else
```

`pwd` (or `cd` alone in PowerShell) tells you where you currently are.

</details>

---

## Step 4: create a virtual environment

```bash
python3 -m venv .venv      # Windows PowerShell: python -m venv .venv
```

Nothing visible happens. That is correct.

### What did that do, and why?

A **virtual environment** is a private Python workspace for one project. It is a
folder — here, `.venv` — containing its own copy of Python and its own place to
put packages.

Without one, every package you install goes into one shared pile for your whole
computer. Two projects wanting different versions of the same thing will fight,
and the loser breaks. With one, each project gets its own pile and they cannot
interfere.

The `.venv` folder is disposable. If your environment ever gets into a state you
do not understand, delete it and make a new one. Nothing of yours lives in
there. This is covered in
[Resetting your environment](../troubleshooting/environment-reset.md).

---

## Step 5: activate it

This is the step people forget, so if something stops working later, check this
first.

| Platform | Command |
|---|---|
| **macOS / Linux / WSL** | `source .venv/bin/activate` |
| **Windows PowerShell** | `.venv\Scripts\Activate.ps1` |
| **Windows cmd.exe** | `.venv\Scripts\activate.bat` |

Your prompt changes to show `(.venv)` at the start:

```
(.venv) you@computer:~/moonfield$
```

**That prefix is how you know it worked.** No prefix means not activated.

<details>
<summary><strong>Windows: "running scripts is disabled on this system"</strong></summary>

PowerShell blocks scripts by default. Allow them for your own account:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Answer `Y`. This affects only your user account, not the whole machine, and it
still requires downloaded scripts to be signed. Then try activating again.

</details>

<details>
<summary><strong>Do I have to do this every time?</strong></summary>

Yes — once per new terminal window. It is not permanent, and that is on
purpose: it means "use this project's Python", and it should stop applying when
you go and work on something else.

If you forget, you will usually see `command not found: moonfield`. Just
activate and try again.

</details>

---

## Step 6: install Moonfield

```bash
pip install -e .
```

The `-e` means "editable": it links to the source rather than copying it, so if
you change the code — and you will, that is the point — your changes take effect
immediately without reinstalling.

The `.` means "the project in this folder".

Expect a few lines ending in something like:

```
Successfully installed moonfield-0.1.0
```

Moonfield has **no runtime dependencies**. Nothing else gets downloaded. That is
deliberate: it means this step almost cannot fail, and it means every formula
in the project is one you can go and read.

---

## Step 7: check it worked

```bash
moonfield doctor
```

This is Moonfield's self-check. It reports your Python version, whether your
virtual environment is active, your timezone, the current UTC time, your saved
location, and it runs the phase engine once to prove the maths works.

It ends with either:

```
Result: everything essential is working.
```

or a list of `PROBLEM:` lines, each with a fix.

> **What `doctor` does not tell you.** It confirms your computer *knows* what
> timezone it is in and can do the arithmetic. It cannot confirm your clock is
> actually set correctly — nothing on your own machine can check its own clock.
> If your predictions are consistently a few minutes off, that is worth
> investigating. See [Time and place](../01-time-and-place/).

---

## Step 8: tell it where you are

```bash
moonfield config set-location --lat 51.4779 --lon -0.0015 \
    --name "Greenwich" --timezone Europe/London
```

Replace those numbers with your own.

- **Latitude:** north positive, south negative. Sydney is `-33.8688`.
- **Longitude:** **east positive**, west negative. New York is `-74.006`.

> **The most common mistake in this whole project** is a longitude sign. If your
> results are wildly wrong later — the Sun rising at midnight, the Moon on the
> wrong side of the sky — check this first. Places west of Greenwich (the
> Americas, western Europe, west Africa) have **negative** longitude.

To find your coordinates: open any map website, right-click where you are, and
it will show you two numbers. The first is latitude, the second longitude.

Timezone names look like `Europe/Lisbon`, `America/Chicago`,
`Australia/Sydney`, `Africa/Nairobi`. You can leave `--timezone` off and it
will use your computer's setting.

Check it:

```bash
moonfield config show
```

---

## You are done

```bash
moonfield phase
```

If you see a Moon, you have a working install.

Next: [Your first command](first-command.md), which explains what that output
actually means.

---

## Quick reference

Every new terminal session:

```bash
cd moonfield                     # go to the project
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
moonfield phase                  # do astronomy
```

To leave the virtual environment: `deactivate`.

---

## Checkpoint

- [ ] I can open a terminal on my system
- [ ] I know how to check my Python version
- [ ] I know what a virtual environment is and why it exists
- [ ] I can activate mine, and I know I must do it each session
- [ ] `moonfield doctor` reports everything working
- [ ] I have saved my location, with the right longitude sign
- [ ] I know `doctor` checks configuration, not clock accuracy
- [ ] I know where to go when I get stuck

## Getting stuck?

- [Getting Unstuck](../troubleshooting/getting-unstuck.md) — by symptom
- [Resetting your environment](../troubleshooting/environment-reset.md) — start clean
- [Windows-specific problems](../troubleshooting/windows.md)
- [macOS-specific problems](../troubleshooting/macos.md)
- [Linux and WSL problems](../troubleshooting/linux.md)
- [Discussions](https://github.com/moonfield/moonfield/discussions) — ask a human

## Go deeper

- [What a virtual environment really is](../background/virtual-environments.md)
- [What `pip install -e .` actually does](../background/editable-installs.md)
