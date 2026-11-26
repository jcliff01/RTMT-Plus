"""Tests for RTMT integration, using a synthetic install (no Cisco files are committed)."""
from pathlib import Path

import pytest

from rtmt_plus import cli, rtmt
from rtmt_plus.search import parse_cause


def make_install(root: Path, trace_dir: Path | None = None) -> Path:
    (root / "global").mkdir(parents=True)
    (root / "conf").mkdir()
    (root / "JRtmt.jar").write_bytes(b"")
    (root / "run.sh").write_text("echo rtmt\n")
    (root / "global" / "ServerVersion.xml").write_text(
        "<rtmtproperties><client><version><applet>001</applet>"
        "<control>15.0</control></version></client></rtmtproperties>")
    trace = str(trace_dir) if trace_dir else "this/path/is/not/set"
    (root / "conf" / "rtmt.xml").write_text(
        f"<rtmt><global><parameters><sControllerVersion>15.0(001)</sControllerVersion>"
        f"<TraceDnldPath>{trace}</TraceDnldPath></parameters></global></rtmt>")
    (root / "conf" / "ucmCauseCode.properties").write_text(
        "#synthetic\n16 = Normal call clearing. Explanation: test text\n"
        "31 = Normal, unspecified\nbad line\nabc = ignored\n", encoding="iso-8859-1")
    return root


def test_parse_properties():
    table = rtmt.parse_properties("# c\n1 = One\n2=Two = 2\n\nx = y\n")
    assert table == {1: "One", 2: "Two = 2"}


def test_load_install(tmp_path):
    traces = tmp_path / "traces"
    traces.mkdir()
    install = rtmt.load_install(make_install(tmp_path / "rtmt", traces))
    assert install.version == "15.0(001)"
    assert install.trace_download_path == traces
    assert install.describe(16) == "Normal call clearing"
    assert install.describe("16", short=False).endswith("test text")
    assert install.describe(99) is None
    assert install.describe(None) is None


def test_unset_trace_path(tmp_path):
    assert rtmt.load_install(make_install(tmp_path / "rtmt")).trace_download_path is None


def test_not_an_install(tmp_path):
    with pytest.raises(rtmt.RtmtNotFound):
        rtmt.load_install(tmp_path)


def test_env_var(tmp_path, monkeypatch):
    monkeypatch.setenv(rtmt.ENV_VAR, str(make_install(tmp_path / "rtmt")))
    assert rtmt.load_install().version == "15.0(001)"


def test_java_supported():
    assert rtmt.java_supported("1.8.0_301")
    assert not rtmt.java_supported("1.8.0_291")
    assert not rtmt.java_supported("17.0.9")
    assert not rtmt.java_supported(None)


def test_launch_command(tmp_path):
    install = rtmt.load_install(make_install(tmp_path / "rtmt"))
    assert rtmt.launch_command(install, "nt")[-1].endswith("run.bat")
    assert rtmt.launch_command(install, "posix") == ["bash", str(install.root / "run.sh")]


def test_parse_cause():
    assert parse_cause("Reason: Q.850;cause=16;text=x") == 16
    assert parse_cause("DisconnectCause = 31") == 31
    assert parse_cause("causeValue=41") == 41
    assert parse_cause("because=5") is None
    assert parse_cause("no cause here") is None


def test_cli_decodes_causes_from_rtmt_trace_folder(tmp_path, capsys):
    traces = tmp_path / "traces"
    traces.mkdir()
    (traces / "sdl001.txt").write_text("2026-11-17 10:00:00 SIP BYE Reason: Q.850;cause=16\n")
    home = make_install(tmp_path / "rtmt", traces)
    assert cli.main(["--rtmt-home", str(home), "-q", "BYE"]) == 0
    assert "[cause 16: Normal call clearing]" in capsys.readouterr().out
    assert cli.main(["--rtmt-home", str(home), "-q", "BYE", "--format", "csv"]) == 0
    out = capsys.readouterr().out
    assert out.splitlines()[0] == "path,line,timestamp,call_id,cause,cause_text,text"
    assert "Normal call clearing" in out


def test_cli_rtmt_info(tmp_path, capsys):
    assert cli.main(["--rtmt-info", "--rtmt-home", str(make_install(tmp_path / "rtmt"))]) == 0
    assert "15.0(001)" in capsys.readouterr().out


def test_cli_requires_query(tmp_path):
    with pytest.raises(SystemExit):
        cli.main([str(tmp_path)])
