import json

import pytest
from PIL import Image


@pytest.fixture
def env_setup(monkeypatch):
    env = {
        "COLPALI_TOKEN": "test-token",
        "VLLM_URL": "http://localhost",
        "COLPALI_BASE_URL": "http://localhost",
        "VLLM_API_KEY": "dummy",
    }
    for k, v in env.items():
        monkeypatch.setenv(k, v)


def test_caseinfo_save_and_update(tmp_path, env_setup, monkeypatch):
    from importlib import reload

    import np_ocr.api as api
    reload(api)
    monkeypatch.setattr(api.settings, "CASE_INFO_FILENAME", "case_info.json", raising=False)

    case_dir = tmp_path / "case"
    case_dir.mkdir()
    case = api.CaseInfo(
        name="mycase",
        status="processing",
        number_of_pdfs=1,
        files=["file.pdf"],
        case_dir=case_dir,
    )
    case.save()
    with open(case_dir / "case_info.json") as f:
        data = json.load(f)
    assert data["status"] == "processing"

    case.update_status("done")
    with open(case_dir / "case_info.json") as f:
        data = json.load(f)
    assert data["status"] == "done"


def test_call_vllm_parses_response(env_setup, monkeypatch):
    from importlib import reload

    import np_ocr.search as search
    reload(search)

    class FakeCompletions:
        @staticmethod
        def parse(*args, **kwargs):
            class Msg:
                parsed = search.ImageAnswer(answer="ok")
            class Choice:
                message = Msg()
            class Completion:
                choices = [Choice()]
            return Completion()

    class FakeOpenAI:
        def __init__(self, base_url=None, api_key=None):
            pass
        class Beta:
            class Chat:
                completions = FakeCompletions()
            chat = Chat()
        beta = Beta()

    monkeypatch.setattr(search, "OpenAI", FakeOpenAI)
    img = Image.new("RGB", (10, 10))
    result = search.call_vllm(img, "hi", base_url="http://x", api_key="y", model="m")
    assert result.answer == "ok"

