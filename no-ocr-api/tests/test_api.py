import os
import shutil
import pytest
from fastapi.testclient import TestClient
from api import app 

@pytest.fixture
def client():
    """
    A pytest fixture that creates a TestClient for our FastAPI 'app'.
    It also cleans up any residual storage after tests run.
    """

    with TestClient(app) as c:
        yield c

    if os.path.exists("storage"):
        shutil.rmtree("storage")

