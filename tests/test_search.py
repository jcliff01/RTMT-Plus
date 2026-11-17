from datetime import datetime
import gzip
import pytest

from rtmt_plus.search import iter_files, parse_call_id, parse_timestamp, search

def test_timestamp():
    assert parse_timestamp("2026-11-17 10:11:12.123 ERROR") == datetime(2026, 11, 17, 10, 11, 12, 123000)
    assert parse_timestamp("no date") is None

def test_call_id():
    assert parse_call_id("Call-ID: abc-123@node") == "abc-123@node"

def test_search_text_regex_time_and_call_id(tmp_path):
    log = tmp_path / "cucm.log"
    log.write_text(
        "2026-11-17 10:00:00 INFO Call-ID: a-1 connected\n"
        "2026-11-17 10:01:00 ERROR Call-ID: a-1 disconnected\n"
        "2026-11-17 10:02:00 ERROR Call-ID: b-2 failed\n",
        encoding="utf-8")
    matches = list(search([tmp_path], "error", since=datetime(2026, 11, 17, 10, 1), call_id="a-1"))
    assert len(matches) == 1
    assert matches[0].line == 2
    assert matches[0].call_id == "a-1"
    assert len(list(search([tmp_path], "ERROR.*failed", regex=True))) == 1

def test_gzip_and_limit(tmp_path):
    path = tmp_path / "trace.gz"
    with gzip.open(path, "wt") as handle:
        handle.write("error first\nerror second\n")
    assert len(list(search([path], "ERROR", limit=1))) == 1

def test_missing_path(tmp_path):
    with pytest.raises(FileNotFoundError):
        list(iter_files([tmp_path / "missing"]))

def test_empty_query(tmp_path):
    with pytest.raises(ValueError):
        list(search([tmp_path], ""))

def test_skip_unrelated_extensions(tmp_path):
    (tmp_path / "secret.env").write_text("error")
    assert list(search([tmp_path], "error")) == []
