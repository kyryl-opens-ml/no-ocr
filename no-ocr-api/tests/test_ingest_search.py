import os
import shutil
import sys
import types
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

sys.path.append(str(Path(__file__).resolve().parents[1]))


@pytest.fixture
def client(monkeypatch):
    env = {
        "COLPALI_TOKEN": "test-token",
        "VLLM_URL": "http://localhost",
        "COLPALI_BASE_URL": "http://localhost",
        "VLLM_API_KEY": "dummy",
    }
    for k, v in env.items():
        monkeypatch.setenv(k, v)

    fake_module = types.ModuleType("lancedb")
    fake_module.connect = lambda *a, **kw: None
    sys.modules["lancedb"] = fake_module

    from np_ocr.api import app

    with TestClient(app) as c:
        yield c

    if os.path.exists("storage"):
        shutil.rmtree("storage")


class FakeDataset:
    def __init__(self, data):
        self.data = list(data)

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]


@pytest.fixture
def fake_dataset_class(monkeypatch):
    import np_ocr.data as data

    def fake_from_list(lst):
        return FakeDataset(lst)

    monkeypatch.setattr(data, "Dataset", types.SimpleNamespace(from_list=staticmethod(fake_from_list)))
    return data


def test_pdfs_to_hf_dataset(monkeypatch, tmp_path, fake_dataset_class):
    from importlib import reload

    data = fake_dataset_class
    reload(data)

    def fake_convert_from_path(*args, **kwargs):
        return [Image.new("RGB", (10, 10)), Image.new("RGB", (10, 10))]

    class FakePage:
        def __init__(self, text):
            self.text = text

        def extract_text(self):
            return self.text

    class FakeReader:
        def __init__(self, _):
            self.pages = [FakePage("a"), FakePage("b")]

    monkeypatch.setattr(data, "convert_from_path", fake_convert_from_path)
    monkeypatch.setattr(data, "PdfReader", FakeReader)

    (tmp_path / "doc1.pdf").write_bytes(b"%PDF-1.4")
    (tmp_path / "doc2.pdf").write_bytes(b"%PDF-1.4")

    dataset = data.pdfs_to_hf_dataset(tmp_path)
    assert len(dataset) == 4
    assert dataset[0]["pdf_name"] == "doc1.pdf"
    assert dataset[0]["pdf_page"] == 1


def test_search_images_by_text(monkeypatch):
    from importlib import reload

    import np_ocr.search as search
    reload(search)

    class FakeTable:
        def search(self, *_):
            class Limiter:
                def limit(self, *_):
                    class Selector:
                        def select(self, *_):
                            return self

                        def to_list(self):
                            return [{"_distance": 0.1, "index": 0, "pdf_name": "x.pdf", "pdf_page": 1}]

                    return Selector()

            return Limiter()

    class FakeDB:
        def open_table(self, _):
            return FakeTable()

    monkeypatch.setattr(search.lancedb, "connect", lambda *_: FakeDB())

    class FakeColPali:
        def query_text(self, _):
            return {"embedding": [0.0]}

    client = search.SearchClient(storage_dir="s", vector_size=1, base_url="b", token="t")
    client.colpali_client = FakeColPali()
    res = client.search_images_by_text("q", case_name="c", user_id="u", top_k=1)
    assert res[0]["pdf_name"] == "x.pdf"


def test_ai_search_dataset_missing(client, monkeypatch):
    from np_ocr import api as api_module

    monkeypatch.setattr(api_module, "search_client", types.SimpleNamespace(search_images_by_text=lambda *a, **k: []))

    response = client.post(
        "/search",
        data={"user_query": "foo", "user_id": "user", "case_name": "case"},
    )
    assert response.status_code == 404


def test_vllm_call_missing_dataset(client):
    response = client.post(
        "/vllm_call",
        data={
            "user_query": "foo",
            "user_id": "user",
            "case_name": "case",
            "pdf_name": "x.pdf",
            "pdf_page": 1,
        },
    )
    assert response.status_code == 404


def test_vllm_call_image_not_found(client, monkeypatch, tmp_path):
    from np_ocr import api as api_module

    ds_path = tmp_path / "storage/user/case/hf_dataset"
    ds_path.mkdir(parents=True)

    fake_dataset = FakeDataset([
        {"pdf_name": "a.pdf", "pdf_page": 1, "image": Image.new("RGB", (10, 10))}
    ])

    monkeypatch.setattr(api_module, "load_from_disk", lambda *_: fake_dataset)
    monkeypatch.setattr(
        api_module,
        "settings",
        types.SimpleNamespace(
            STORAGE_DIR=str(tmp_path / "storage"),
            HF_DATASET_DIRNAME="hf_dataset",
            VLLM_URL="http://x",
            VLLM_API_KEY="k",
            VLLM_MODEL="m",
        ),
    )
    monkeypatch.setattr(api_module, "call_vllm", lambda *a, **kw: api_module.ImageAnswer(answer="ok"))

    response = client.post(
        "/vllm_call",
        data={
            "user_query": "foo",
            "user_id": "user",
            "case_name": "case",
            "pdf_name": "not.pdf",
            "pdf_page": 2,
        },
    )
    assert response.status_code == 404

