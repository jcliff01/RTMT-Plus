# Windows EXE build

The Windows desktop application is packaged using PyInstaller on a GitHub-hosted Windows runner.

## Download a CI build

1. Open the repository's **Actions** tab.
2. Choose **Build Windows EXE**.
3. Choose the latest successful run (or select **Run workflow**).
4. Under **Artifacts**, download **RTMT-Plus-Windows-x64**.
5. Unzip it, then launch **RTMT-Plus.exe**.

GitHub requires you to be signed in to download workflow artifacts. Artifacts are retained for 30 days. This build is not code-signed; Windows SmartScreen may warn about an unknown publisher. Only run builds you trust.

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
