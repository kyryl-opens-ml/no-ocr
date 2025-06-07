import os
import shutil
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))


@pytest.fixture
def client(monkeypatch):
    """Return a TestClient for the FastAPI app with test environment vars."""

    env = {
        "COLPALI_TOKEN": "test-token",
        "VLLM_URL": "http://localhost",
        "COLPALI_BASE_URL": "http://localhost",
        "VLLM_API_KEY": "dummy",
    }
    for key, value in env.items():
        monkeypatch.setenv(key, value)

    import types
    fake_module = types.ModuleType("lancedb")
    fake_module.connect = lambda *a, **kw: None
    sys.modules["lancedb"] = fake_module

    from np_ocr.api import app

    with TestClient(app) as c:
        yield c

    if os.path.exists("storage"):
        shutil.rmtree("storage")

def test_health_check(client):
    """
    Test the health check endpoint to ensure the API is running.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.skip(reason="End-to-end test requires external services")
def test_end2end(client):
    # Step 1: Create a case with a document
    import uuid

    case_name = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    print(f"Creating case '{case_name}' for user '{user_id}'")
    files = {"files": ("InfraRed-Report.pdf", open("data/InfraRed-Report.pdf", "rb"), "application/pdf")}
    response = client.post("/create_case", data={"user_id": user_id, "case_name": case_name}, files=files)
    print(f"Response status code for create_case: {response.status_code}")
    assert response.status_code == 200
    case_info = response.json()
    print(f"Case info after creation: {case_info}")
    assert case_info["status"] == "processing"

    # Step 2: Poll the get_case endpoint until the status is 'done'
    import time
    max_retries = 10
    for attempt in range(max_retries):
        print(f"Polling get_case, attempt {attempt + 1}")
        response = client.get(f"/get_case/{case_name}", params={"user_id": user_id})
        print(f"Response status code for get_case: {response.status_code}")
        assert response.status_code == 200
        case_info = response.json()
        print(f"Case info during polling: {case_info}")
        if case_info["status"] == "done":
            print("Case processing completed.")
            break
        time.sleep(1)  # Wait for a second before retrying
    else:
        pytest.fail("Case processing did not complete in time.")

    # Step 3: Call the search endpoint
    print(f"Calling search endpoint for case '{case_name}'")
    response = client.post(
        "/search",
        data={
            "user_query": "Margin between the SaaS and Infra companies?",
            "user_id": user_id,
            "case_name": case_name,
        },
    )
    print(f"Response status code for search: {response.status_code}")
    assert response.status_code == 200
    search_results = response.json()
    assert "search_results" in search_results
    assert len(search_results["search_results"]) > 0

    # Check the output schema
    for result in search_results["search_results"]:
        assert "score" in result
        assert "pdf_name" in result
        assert "pdf_page" in result
        assert isinstance(result["score"], float)
        assert isinstance(result["pdf_name"], str)
        assert isinstance(result["pdf_page"], int)

    # Step 4: Call the vllm endpoint with random pages from search results
    import random
    random_result = random.choice(search_results["search_results"])
    pdf_name = random_result["pdf_name"]
    pdf_page = random_result["pdf_page"]
    print(f"Calling vllm endpoint for PDF '{pdf_name}' page {pdf_page}")
    response = client.post("/vllm_call", data={
        "user_query": "AI",
        "user_id": user_id,
        "case_name": case_name,
        "pdf_name": pdf_name,
        "pdf_page": pdf_page
    })
    print(f"Response status code for vllm_call: {response.status_code}")
    assert response.status_code == 200
    vllm_result = response.json()
    assert "answer" in vllm_result
    print(f"VLLM result: {vllm_result['answer']}")

    # Step 5: Delete the case
    print(f"Deleting case '{case_name}' for user '{user_id}'")
    response = client.delete(f"/delete_case/{case_name}", params={"user_id": user_id})
    print(f"Response status code for delete_case: {response.status_code}")
    assert response.status_code == 200
    delete_result = response.json()
    assert "message" in delete_result
    print(f"Delete result: {delete_result['message']}")


def test_get_case_not_found(client):
    response = client.get("/get_case/nonexistent", params={"user_id": "user"})
    assert response.status_code == 404


def test_search_no_collections(client):
    response = client.post(
        "/search",
        data={"user_query": "foo", "user_id": "user", "case_name": "case"},
    )
    assert response.status_code == 404
