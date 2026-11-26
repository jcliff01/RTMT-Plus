"""Integration with a locally installed Cisco Unified RTMT client (tested layout: RTMT 15).

RTMT Plus never bundles, modifies, or redistributes Cisco software. Everything here
reads files from the user's own licensed RTMT installation at runtime:

* ``global/ServerVersion.xml`` / ``conf/rtmt.xml`` -> client version
* ``conf/rtmt.xml`` ``TraceDnldPath`` -> where RTMT saves collected traces
* ``conf/*CauseCode.properties`` / ``*CallDispositions.properties`` -> code catalogs
* ``run.bat`` / ``run.sh`` -> launching RTMT from its own folder
"""
from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

ENV_VAR = "RTMT_HOME"
MARKER = "JRtmt.jar"
MAX_CONFIG_BYTES = 2 * 1024 * 1024
# Catalog name -> properties file name in <RTMT>/conf
CATALOG_FILES = {
    "ucm": "ucmCauseCode.properties",
    "acs": "acsCauseCode.properties",
    "cvp": "cvpCauseCode.properties",
    "ea": "eaCauseCode.properties",
    "ucce": "ucceCauseCode.properties",
    "ucce-disposition": "ucceCallDispositions.properties",
    "uccx": "uccxCauseCode.properties",
}
_UNSET = "this/path/is/not/set"


class RtmtNotFound(FileNotFoundError):
    """Raised when a folder is not a usable RTMT installation."""


@dataclass
class RtmtInstall:
    root: Path
    version: str | None = None
    trace_download_path: Path | None = None
    catalogs: dict[str, dict[int, str]] = field(default_factory=dict)

    def describe(self, code: int | str | None, catalog: str = "ucm", *, short: bool = True) -> str | None:
        """Return the text RTMT uses for a cause code, or None if unknown."""
        if code is None:
            return None
        try:
            number = int(code)
        except (TypeError, ValueError):
            return None
        text = self.catalogs.get(catalog, {}).get(number)
        if text and short:
            text = text.split(". Explanation:", 1)[0].strip()
        return text

    @property
    def launcher(self) -> Path:
        return self.root / ("run.bat" if os.name == "nt" else "run.sh")


def _read_text(path: Path) -> str:
    if path.stat().st_size > MAX_CONFIG_BYTES:
        raise ValueError(f"Config file too large: {path}")
    return path.read_text(encoding="iso-8859-1")


def parse_properties(text: str) -> dict[int, str]:
    """Parse RTMT's simple ``code = text`` properties files (numeric keys only)."""
    table: dict[int, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "!")) or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key.isdigit():
            table[int(key)] = value.strip()
    return table


def _xml_text(path: Path, tag: str) -> str | None:
    try:
        root = ET.fromstring(_read_text(path))
    except (OSError, ValueError, ET.ParseError):
        return None
    node = root.find(f".//{tag}")
    return node.text.strip() if node is not None and node.text and node.text.strip() else None


def read_version(root: Path) -> str | None:
    server = root / "global" / "ServerVersion.xml"
    if server.is_file():
        control = _xml_text(server, "control")
        applet = _xml_text(server, "applet")
        if control:
            return f"{control}({applet})" if applet else control
    conf = root / "conf" / "rtmt.xml"
    return _xml_text(conf, "sControllerVersion") if conf.is_file() else None


def read_trace_download_path(root: Path) -> Path | None:
    conf = root / "conf" / "rtmt.xml"
    value = _xml_text(conf, "TraceDnldPath") if conf.is_file() else None
    if not value or value == _UNSET:
        return None
    return Path(value).expanduser()


def load_install(path: str | Path | None = None) -> RtmtInstall:
    """Load an RTMT install from *path*, or from the RTMT_HOME environment variable."""
    raw = path if path is not None else os.environ.get(ENV_VAR)
    if not raw:
        raise RtmtNotFound(f"No RTMT folder given; pass --rtmt-home or set {ENV_VAR}")
    root = Path(raw).expanduser()
    if not (root / MARKER).is_file():
        raise RtmtNotFound(f"Not an RTMT folder (missing {MARKER}): {root}")
    catalogs: dict[str, dict[int, str]] = {}
    for name, filename in CATALOG_FILES.items():
        file = root / "conf" / filename
        if file.is_file():
            try:
                catalogs[name] = parse_properties(_read_text(file))
            except (OSError, ValueError):
                continue
    return RtmtInstall(root=root.resolve(), version=read_version(root),
                       trace_download_path=read_trace_download_path(root), catalogs=catalogs)


def find_java() -> str | None:
    """Return the ``java -version`` string RTMT will see, or None if Java is missing."""
    java = shutil.which("java")
    if not java:
        return None
    try:
        result = subprocess.run([java, "-version"], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    match = re.search(r'version "([^"]+)"', result.stderr + result.stdout)
    return match.group(1) if match else None


def java_supported(version: str | None) -> bool:
    """RTMT 15's launchers require Java 1.8.0 update 300 or newer (Java 8 only)."""
    match = re.match(r"1\.8\.0_(\d+)", version or "")
    return bool(match and int(match.group(1)) >= 300)


def launch_command(install: RtmtInstall, platform: str | None = None) -> list[str]:
    platform = platform or os.name
    if platform == "nt":
        return ["cmd.exe", "/c", str(install.root / "run.bat")]
    return ["bash", str(install.root / "run.sh")]


def launch(install: RtmtInstall) -> subprocess.Popen:
    """Start RTMT with its own folder as the working directory.

    Cisco's run.bat / run.sh use relative ``./lib`` paths, so they fail when started
    from anywhere else (for example from a shortcut with no "Start in" folder).
    """
    if not install.launcher.is_file():
        raise RtmtNotFound(f"Launcher missing: {install.launcher}")
    kwargs: dict = {"cwd": str(install.root)}
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
    else:
        kwargs["start_new_session"] = True
    return subprocess.Popen(launch_command(install), **kwargs)  # noqa: S603 - fixed argv
