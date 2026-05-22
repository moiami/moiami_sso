from pathlib import Path

import pytest

from src.constants import key_load


def test_key_load_reads_and_strips_file(tmp_path: Path) -> None:
    key_file = tmp_path / "key.pem"
    key_file.write_text("  test-key-content  \n", encoding="utf-8")

    assert key_load(str(key_file)) == "test-key-content"


def test_key_load_raises_when_file_missing(tmp_path: Path) -> None:
    with pytest.raises(Exception):
        key_load(str(tmp_path / "missing.pem"))
