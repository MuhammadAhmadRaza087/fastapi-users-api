import os
import tempfile
from pathlib import Path

import pytest

# Must be set before the app is imported so it uses a throwaway database.
_tmp = Path(tempfile.mkdtemp())
os.environ["DATABASE_URL"] = f"sqlite:///{(_tmp / 'test.db').as_posix()}"
os.environ["SEED_ON_STARTUP"] = "true"
os.environ["SEED_COUNT"] = "25"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
