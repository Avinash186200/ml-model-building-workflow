"""Checks every notebook: valid JSON, no saved outputs, no credentials, no local paths."""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted(p for p in ROOT.rglob("*.ipynb") if ".ipynb_checkpoints" not in p.parts)
SECRET = re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*[\"'](?!your)[A-Za-z0-9_\-]{12,}[\"']")
LOCAL_PATH = re.compile(r"(?i)\b[A-Z]:[\\/]|/Users/")


def test_there_are_notebooks():
    assert NOTEBOOKS


@pytest.mark.parametrize("nb_path", NOTEBOOKS, ids=lambda p: str(p.relative_to(ROOT)))
def test_notebook_is_clean(nb_path):
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    assert "cells" in nb
    for cell in nb["cells"]:
        src = "".join(cell.get("source", []))
        assert not SECRET.search(src), "credential-like assignment"
        assert not LOCAL_PATH.search(src), "local path"
        if cell.get("cell_type") == "code":
            # original/ is an output-free archive; maintained notebooks are committed without outputs too.
            assert not cell.get("outputs"), "notebooks must be committed with outputs stripped"
            assert cell.get("execution_count") is None, "notebooks must be committed unexecuted"
