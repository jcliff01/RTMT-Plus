# Windows EXE build

The Windows desktop application is packaged using PyInstaller on a GitHub-hosted Windows runner.

## Download

Merges to `main` publish the program as the [latest release](https://github.com/jcliff01/RTMT-Plus/releases/latest): download **RTMT-Plus.exe** there, no GitHub account needed. Every build is also kept for 30 days as an artifact named **RTMT-Plus-Windows-x64** on the workflow's run page under **Actions → Build Windows EXE** (downloading artifacts needs a GitHub sign-in).

The program isn't code-signed, so Windows SmartScreen may warn about an unknown publisher: click **More info**, then **Run anyway**. Only run builds from this repository.

## Build locally on Windows

Requires Python 3.12 and a supported Windows x64 environment.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -e ".[desktop,dev]"
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m pip install "pyinstaller>=6.11,<7"
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name RTMT-Plus --collect-all PySide6 src/rtmt_plus/desktop_launcher.py
```

The result is `dist\RTMT-Plus.exe`.

## Limitations

- Windows EXE is a standalone GUI, not a Cisco RTMT plugin or installer.
- The GUI currently performs synchronous text search; very large log sets may temporarily block the window.
- Search runs on local files only; no live CUCM connectivity yet.
- CI checks package creation, but does not currently run automated GUI smoke tests.
- Do not include production logs or credentials in public bug reports.
