import os
from pathlib import Path
import pytest

@pytest.fixture(autouse=True)
def set_project_root(monkeypatch):
    root = Path(__file__).resolve().parent.parent
    monkeypatch.chdir(root)
