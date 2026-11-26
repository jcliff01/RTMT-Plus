# Getting started

Step-by-step setup for RTMT Plus with Cisco RTMT 15 on Windows. macOS/Linux notes are at the end.

RTMT Plus is a companion to Cisco RTMT. It reads your own RTMT install at runtime and never
includes Cisco files. Details: [RTMT_INTEGRATION.md](RTMT_INTEGRATION.md).

## 1. Install Java 8 (for RTMT)

RTMT 15 only runs on **Java 8, version 1.8.0_300 or newer**. Java 11, 17 and 21 are rejected.
For certificate-based login you also need **JavaFX**, so use a Java 8 build that includes it
(e.g. Oracle JDK 8, or Azul Zulu 8 "JDK FX").

Check it:

```powershell
java -version    # must show 1.8.0_300 or higher
```

If it shows another version, put the Java 8 `bin` folder first on your `PATH`.

## 2. Unzip RTMT 15

Unzip the Cisco RTMT package to a fixed folder, for example `C:\Cisco\RTMT15`.
That folder must contain `JRtmt.jar`. Don't move it afterwards.

## 3. Install RTMT Plus

Requires **Python 3.10 or newer** ([python.org](https://www.python.org/downloads/); tick "Add to PATH").

```powershell
py -m pip install "rtmt-plus[desktop] @ git+https://github.com/jcliff01/RTMT-Plus"
```

Prefer an EXE? See [WINDOWS_BUILD.md](WINDOWS_BUILD.md). The EXE is the desktop app only,
so skip step 4 and use the **RTMT folder…** button instead.

## 4. Point RTMT Plus at RTMT (once)

```powershell
setx RTMT_HOME "C:\Cisco\RTMT15"
```

Close and reopen your terminal. `setx` only affects new windows.

## 5. Check the setup

```powershell
rtmt-plus --rtmt-info
```

Expected output:

```text
RTMT folder:     C:\Cisco\RTMT15
RTMT version:    15.0(001)
Trace downloads: C:\Users\<you>\Cisco\RTMT\TraceCollection (exists)
Cause catalogs:  acs, cvp, ea, ucce, ucce-disposition, uccx, ucm
Java:            1.8.0_xxx - OK
```

## 6. Use it

```powershell
rtmt-plus --launch-rtmt                     # start Cisco RTMT
rtmt-plus -q "cause="                       # search RTMT's downloaded traces, causes decoded
rtmt-plus C:\logs -q "SIP/2.0 503"          # search any folder
rtmt-plus -q "Q.850" --format csv > out.csv # export (adds cause + cause_text columns)
rtmt-plus-desktop                           # desktop app
```

Typical workflow: collect traces in RTMT (**Trace & Log Central → Collect Files**), then search
them with RTMT Plus.

In the desktop app, click **RTMT folder…** once (it's remembered), then **Use RTMT traces**
and **Search**, or **Launch RTMT**.

More search options:

```powershell
rtmt-plus -q "Call-ID" --since 2026-11-17T09:00:00 --until 2026-11-17T10:00:00
rtmt-plus -q "disconnect|timeout" --regex --limit 500
rtmt-plus -q "cause" --cause-catalog cvp    # catalogs: ucm (default), acs, cvp, ea, ucce, ucce-disposition, uccx
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `rtmt-plus` not found | Reopen the terminal, or run `py -m rtmt_plus.cli` instead. |
| "Not an RTMT folder" | `RTMT_HOME` must be the folder that contains `JRtmt.jar`. |
| RTMT doesn't start | `--rtmt-info` will show the Java problem. You need Java 1.8.0_300+ first on `PATH`. |
| Trace folder "not found" | Collect traces in RTMT once. It creates the folder on first save. |
| Certificate login fails | Your Java 8 build is missing JavaFX. Install a JDK FX build. |

## macOS / Linux

- Set the folder with `export RTMT_HOME=~/rtmt15` (add it to `~/.bashrc` or `~/.zshrc`).
- RTMT's `run.sh` needs **bash**. `--launch-rtmt` already uses bash.
- If you used RTMT's `genkeystore.sh` for certificate login, clean up afterwards:
  `rm -f ~/.jrtmt/temp.* && chmod 600 ~/.jrtmt/*` (the script leaves a decrypted private key behind).

## For developers

```bash
git clone https://github.com/jcliff01/RTMT-Plus && cd RTMT-Plus
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
python -m pip install -e ".[desktop,dev]"
python -m pytest
```

Never commit RTMT files, customer logs, or credentials.

## Current limitations

- Search streams through files and isn't indexed yet, so very large folders are slow. The desktop app may freeze while it searches them.
- Timestamp parsing recognizes ISO-style dates only. Call-ID and cause detection are heuristic.
- No live CUCM connection or automatic root-cause diagnosis yet.
