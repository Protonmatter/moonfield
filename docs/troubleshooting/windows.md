# Windows

Moonfield supports Windows natively (PowerShell) and through WSL. Both work.
Pick one and stay with it — mixing them is where confusion starts.

## Which should I use?

**Native PowerShell** — simpler, no extra install, fine for everything in this
curriculum. Recommended if you are new.

**WSL** — a real Linux environment inside Windows. Worth it if you already use
Linux tooling, or want commands in tutorials to work verbatim.

Note that they have **separate filesystems and separate Python installs**. A
venv created in PowerShell will not work in WSL.

## "python is not recognised"

Windows ships a stub that opens the Microsoft Store. Install real Python from
python.org and **tick "Add Python to PATH"** on the first screen.

Check:
```powershell
python --version
```

If it still fails, close and reopen PowerShell — PATH changes need a new
session.

## "cannot be loaded because running scripts is disabled"

Activating a venv runs a script, and Windows blocks that by default.

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

This applies to your user only, not the whole machine, and allows local scripts
while still requiring downloaded ones to be signed. It is the standard
developer setting.

## "moonfield is not recognised" after installing

The venv is probably not active. Your prompt should start with `(.venv)`.

```powershell
.\.venv\Scripts\Activate.ps1
```

Note the backslashes and the leading `.\` — PowerShell will not run a script in
the current directory without it.

## Terminal shows boxes instead of the Moon

The ASCII art needs a Unicode-capable font. Windows Terminal (from the
Microsoft Store) handles it; the old `consolehost` window often does not.

Or just:
```powershell
moonfield phase --no-art
```

## Paths

PowerShell accepts forward slashes in most places, but tutorials written for
Linux may assume `/home/you`. Your equivalent is `$HOME` or
`C:\Users\YourName`.

Config lives in `%APPDATA%\moonfield\config.json`:
```powershell
moonfield config path
```

## Timezone

Windows stores timezones differently from Unix. Python's `zoneinfo` needs the
IANA database:

```powershell
pip install tzdata
```

This is installed automatically by Moonfield on Windows, but if you see
`ZoneInfoNotFoundError`, that is the fix.

## See also

- [Getting unstuck](getting-unstuck.md) · [Environment reset](environment-reset.md)
- [Setup](../00-start-here/setup.md)
