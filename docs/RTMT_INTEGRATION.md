# Using RTMT Plus with Cisco RTMT 15

RTMT Plus works **alongside** your own licensed copy of Cisco Unified RTMT. It reads
files from your RTMT folder at runtime; it never bundles, modifies, or redistributes
Cisco software. Cisco's license forbids redistribution, so **never commit RTMT files
(JARs, configs, or the zip) to this repository** — `.gitignore` blocks the common ones.

## What RTMT Plus reads from your RTMT folder

| RTMT file | Used for |
|---|---|
| `JRtmt.jar` | Recognising the folder as an RTMT install |
| `global/ServerVersion.xml`, `conf/rtmt.xml` | Showing the RTMT version (e.g. `15.0(001)`) |
| `conf/rtmt.xml` → `TraceDnldPath` | Default folder to search: where RTMT saves collected traces |
| `conf/*CauseCode.properties`, `conf/ucceCallDispositions.properties` | Decoding cause codes in search results |
| `run.bat` / `run.sh` | Launching RTMT from its own folder |

Cause-code catalogs: `ucm` (default), `acs`, `cvp`, `ea`, `ucce`, `ucce-disposition`, `uccx`.

## Setup

Point RTMT Plus at the folder that contains `JRtmt.jar`, either per command or once:

```powershell
# Windows PowerShell (persist for your user)
setx RTMT_HOME "C:\Program Files\Cisco\RTMT15"
```

```bash
export RTMT_HOME=~/rtmt15
```

## Commands

```bash
rtmt-plus --rtmt-info                        # version, trace folder, catalogs, Java check
rtmt-plus -q "Q.850"                          # search RTMT's trace download folder
rtmt-plus ./logs -q "cause=" --format csv     # adds cause + cause_text columns
rtmt-plus ./logs -q "cause" --cause-catalog cvp
rtmt-plus --launch-rtmt                       # start Cisco RTMT
```

Text output appends decoded causes, e.g. `... Q.850;cause=16 [cause 16: Normal call clearing]`.

In the desktop app, use **RTMT folder…** (remembered between runs), **Use RTMT traces**,
and **Launch RTMT**.

## RTMT 15 requirements and known quirks

Found while reviewing the RTMT 15 client package:

- **Java 8 only.** `run.bat`/`run.sh` require Java `1.8.0_300` or newer and reject Java 11, 17, and 21.
  JavaFX is needed for certificate-based login. `rtmt-plus --rtmt-info` checks this.
- **Must start from its own folder.** The launchers use relative `./lib` paths, so a shortcut
  without the right "Start in" folder fails. `--launch-rtmt` sets the working folder for you.
- **`run.sh` needs bash**, not `sh` (it has no shebang and uses `[[ ... =~ ]]`).
- **Classpath references files that aren't shipped:** `lib/derby.jar` and `jre/lib/jfxrt.jar`
  (`jfxrt.jar` is in `lib/`). `run.bat` also lists `commons-collection.jar` (actual name:
  `commons-collections.jar`). Usually harmless, but JavaFX features may fail unless your JDK
  includes JavaFX.
- **TLS 1.1 is still enabled** in the launch flags (`-Djdk.tls.client.protocols`).
- **`genkeystore.sh` (Linux certificate login):** on success it leaves the decrypted private
  key (`~/.jrtmt/temp.pem`) and `temp.cert` behind, stores the keystore passphrase in a
  plain-text file, and passes passphrases on the command line. After running it, delete
  `~/.jrtmt/temp.*` and run `chmod 600 ~/.jrtmt/*`.
- **`conf/rtmt.xml` holds personal paths** (e.g. your Windows username in `TraceDnldPath`)
  — another reason not to share the folder.
- Bundled libraries: log4j 2.19 (not affected by Log4Shell); `commons-httpclient` 3.1 and
  Axis 1.x are end-of-life. These are Cisco's to update.
