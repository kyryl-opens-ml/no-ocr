import os
import shutil
import pytest
from fastapi.testclient import TestClient
from api import app  # Adjust the import path as needed

@pytest.fixture
def client():
    """
    A pytest fixture that creates a TestClient for our FastAPI 'app'.
    It also cleans up any residual storage after tests run.
    """
    # Optional: override environment variables or set up a test storage directory if you want an isolated test environment
    # os.environ["STORAGE_DIR"] = "temp_test_storage"

    with TestClient(app) as c:
        yield c

    # Clean up the default or temporary storage
    # If you have set up a custom test STORAGE_DIR, remove that instead.
    if os.path.exists("storage"):
        shutil.rmtree("storage")


def test_create_case(client):
    """
    Test that we can create a new case with a single PDF file.
    """
    response = client.post(
        "/create_case",
        data={"case_name": "test_case"},
        files=[("files", ("test.pdf", b"dummy pdf data", "application/pdf"))],
    )
    assert response.status_code == 200

    resp_json = response.json()
    # Basic checks to confirm the case name, status, and file list in the response
    assert resp_json["name"] == "test_case"
    assert resp_json["status"] == "processing"
    assert "files" in resp_json
    assert resp_json["files"] == ["test.pdf"]


def test_get_cases_empty(client):
    """
    Test the /get_cases when there are no cases yet.
    """
    response = client.get("/get_cases")
    assert response.status_code == 200

    resp_json = response.json()
    # Since no cases have been created prior to this call,
    # response can be "No cases found" or "No case data found" depending on your logic.
    # Adjust your test assertions to match your code’s expected output.
    # For demonstration, we check for "cases" key in response.
    assert "cases" in resp_json
    assert len(resp_json["cases"]) == 0 or resp_json.get("message", "") in [
        "No case data found.",
        "No cases found.",
    ]


def test_create_and_get_case(client):
    """
    Test creating a case, then retrieving it via /get_case/{case_name}.
    """
    # First create the case
    create_response = client.post(
        "/create_case",
        data={"case_name": "my_case"},
        files=[("files", ("doc1.pdf", b"dummy pdf data", "application/pdf"))],
    )
    assert create_response.status_code == 200
    create_json = create_response.json()
    assert create_json["name"] == "my_case"

    # Now get the specific case
    get_case_response = client.get("/get_case/my_case")
    assert get_case_response.status_code == 200
    case_info = get_case_response.json()
    assert case_info["name"] == "my_case"


def test_get_case_not_found(client):
    """
    Test that requesting a non-existing case returns a 404.
    """
    response = client.get("/get_case/unknown_case")
    assert response.status_code == 404
    assert response.json()["detail"] == "Case info not found."


def test_delete_case_not_found(client):
    """
    Test deleting a non-existing case should yield 404 or a relevant error message.
    """
    response = client.delete("/delete_case/does_not_exist")
    assert response.status_code == 404
    resp_json = response.json()
    assert resp_json["detail"] == "Case not found in storage."


def test_delete_all_cases(client):
    """
    Test that we can delete all cases without error.
    """
    # Create at least one case so that there is something to delete
    create_response = client.post(
        "/create_case",
        data={"case_name": "case_to_delete"},
        files=[("files", ("another.pdf", b"dummy pdf data", "application/pdf"))],
    )
    assert create_response.status_code == 200

    del_all_response = client.delete("/delete_all_cases")
    assert del_all_response.status_code == 200

    resp_json = del_all_response.json()
    # Check the message from /delete_all_cases
    assert resp_json["message"] == "All cases have been deleted from storage and Qdrant."

    # Confirm that /get_cases is now empty
    get_cases_response = client.get("/get_cases")
    assert get_cases_response.status_code == 200
    cases_json = get_cases_response.json()
    assert "cases" in cases_json
    assert len(cases_json["cases"]) == 0 or cases_json.get("message", "") in [
        "No case data found.",
        "No cases found.",
    ] 