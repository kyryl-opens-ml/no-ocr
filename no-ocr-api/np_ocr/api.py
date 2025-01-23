import base64
import json
import logging
import os
import shutil
import time
from io import BytesIO
from pathlib import Path
from typing import List

import diskcache as dc
from datasets import load_from_disk
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from np_ocr.data import pdfs_to_hf_dataset
from np_ocr.search import IngestClient, SearchClient, call_vllm


class CustomRailwayLogFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage()
        }
        return json.dumps(log_record)

def get_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    formatter = CustomRailwayLogFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = get_logger()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Settings(BaseSettings):
    STORAGE_DIR: str = "storage"
    CASE_INFO_FILENAME: str = "case_info.json"
    HF_DATASET_DIRNAME: str = "hf_dataset"
    SEARCH_TOP_K: int = 3
    COLPALI_TOKEN: str
    VLLM_URL: str
    COLPALI_BASE_URL: str
    QDRANT_URI: str
    QDRANT_PORT: int
    VECTOR_SIZE: int = 128
    INDEXING_THRESHOLD: int = 100
    QUANTILE: float = 0.99
    TOP_K: int = 5
    QDRANT_HTTPS: bool = True
    VLLM_API_KEY: str
    VLLM_MODEL: str = "Qwen2-VL-7B-Instruct"

    class Config:
        env_file = ".env"


settings = Settings()


class ImageAnswer(BaseModel):
    answer: str

class CaseInfo(BaseModel):
    name: str
    unique_name: str
    status: str
    number_of_PDFs: int
    files: List[str]
    case_dir: Path

    def save(self):
        with open(self.case_dir / settings.CASE_INFO_FILENAME, "w") as json_file:
            json.dump(self.model_dump(), json_file, default=str)

    def update_status(self, new_status: str):
        self.status = new_status
        self.save()


search_client = SearchClient(qdrant_uri=settings.QDRANT_URI, port=settings.QDRANT_PORT, https=settings.QDRANT_HTTPS, top_k=settings.TOP_K, base_url=settings.COLPALI_BASE_URL, token=settings.COLPALI_TOKEN)
ingest_client = IngestClient(qdrant_uri=settings.QDRANT_URI, port=settings.QDRANT_PORT, https=settings.QDRANT_HTTPS, index_threshold=settings.INDEXING_THRESHOLD, vector_size=settings.VECTOR_SIZE, quantile=settings.QUANTILE, top_k=settings.TOP_K, base_url=settings.COLPALI_BASE_URL, token=settings.COLPALI_TOKEN)

cache = dc.Cache("vllm_cache")

def cache_decorator(func):
    def wrapper(*args, **kwargs):
        user_query = kwargs.get("user_query")
        user_id = kwargs.get("user_id")
        case_name = kwargs.get("case_name")
        pdf_name = kwargs.get("pdf_name")
        pdf_page = kwargs.get("pdf_page")

        cache_key = f"{user_id}_{case_name}_{pdf_name}_{pdf_page}_{user_query}"
        if cache_key in cache:
            return cache[cache_key]

        result = func(*args, **kwargs)
        cache[cache_key] = result
        return result
    return wrapper

@cache_decorator
@app.post("/vllm_call")
def vllm_call(
    user_query: str = Form(...), user_id: str = Form(...), case_name: str = Form(...), pdf_name: str = Form(...), pdf_page: int = Form(...)
) -> ImageAnswer:
    logger.info("start vllm_call")
    start_time = time.time()

    """
    Given a user ID, collection name, PDF name, and PDF page number, retrieve the corresponding image
    from the HF dataset and call the VLLM function with this image.
    """
    dataset_path = os.path.join(settings.STORAGE_DIR, user_id, case_name, settings.HF_DATASET_DIRNAME)
    if not os.path.exists(dataset_path):
        raise HTTPException(status_code=404, detail="Dataset for this case not found.")

    dataset = load_from_disk(dataset_path)
    image_data = None

    for data in dataset:
        if data["pdf_name"] == pdf_name and data["pdf_page"] == pdf_page:
            image_data = data["image"]
            break

    if image_data is None:
        raise HTTPException(
            status_code=404, detail="Image not found in the dataset for the given PDF name and page number."
        )

    image_answer = call_vllm(image_data, user_query, settings.VLLM_URL, settings.VLLM_API_KEY, settings.VLLM_MODEL)

    end_time = time.time()
    logger.info(f"done vllm_call, total time {end_time - start_time}")

    return image_answer




class SearchResult(BaseModel):
    score: float
    pdf_name: str
    pdf_page: int
    image_base64: str

class SearchResponse(BaseModel):
    search_results: List[SearchResult]

@app.post("/search", response_model=SearchResponse)
def ai_search(user_query: str = Form(...), user_id: str = Form(...), case_name: str = Form(...)):
    logger.info("start ai_search")
    start_time = time.time()

    """
    Given a user query, user ID, and case name, search relevant images in the Qdrant index
    and return both the results and an LLM interpretation.
    """
    if not os.path.exists(settings.STORAGE_DIR):
        raise HTTPException(status_code=404, detail="No collections found.")

    case_info_path = os.path.join(settings.STORAGE_DIR, user_id, case_name, settings.CASE_INFO_FILENAME)
    if not os.path.exists(case_info_path):
        raise HTTPException(status_code=404, detail="Case info not found.")

    with open(case_info_path, "r") as json_file:
        _ = json.load(json_file)  # case_info is not used directly below

    unique_name =f"{user_id}_{case_name}"
    search_results = search_client.search_images_by_text(user_query, case_name=unique_name, top_k=settings.SEARCH_TOP_K)
    if not search_results:
        return {"message": "No results found."}

    dataset_path = os.path.join(settings.STORAGE_DIR, user_id, case_name, settings.HF_DATASET_DIRNAME)
    if not os.path.exists(dataset_path):
        raise HTTPException(status_code=404, detail="Dataset for this case not found.")

    dataset = load_from_disk(dataset_path)
    search_results_data = []
    for result in search_results.points:
        payload = result.payload
        logger.info(payload)
        score = result.score
        image_data = dataset[payload["index"]]["image"]
        pdf_name = dataset[payload["index"]]["pdf_name"]
        pdf_page = dataset[payload["index"]]["pdf_page"]

        # Convert image to base64 string
        buffered = BytesIO()
        image_data.save(buffered, format="JPEG")
        img_b64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        search_results_data.append(SearchResult(
            score=score,
            pdf_name=pdf_name,
            pdf_page=pdf_page,
            image_base64=img_b64_str
        ))

    end_time = time.time()
    logger.info(f"done ai_search, total time {end_time - start_time}")

    return SearchResponse(search_results=search_results_data)


def process_case(case_info: CaseInfo):
    logger.info("start post_process_case")
    start_time = time.time()

    dataset = pdfs_to_hf_dataset(case_info.case_dir)
    dataset.save_to_disk(case_info.case_dir /  settings.HF_DATASET_DIRNAME)
    ingest_client.ingest(case_info.unique_name, dataset)

    case_info.update_status("done")

    end_time = time.time()
    logger.info(f"done process_case, total time {end_time - start_time}")



@app.post("/create_case")
def create_new_case(
    user_id: str = Form(...),
    files: List[UploadFile] = File(...),
    case_name: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> CaseInfo:
    logger.info("start create_new_case")
    start_time = time.time()

    """
    Create a new case for a specific user, store the uploaded PDFs, and process/ingest them.
    """
    if not files or not case_name or not user_id:
        raise HTTPException(status_code=400, detail="No files, case name, or user ID provided.")

    case_dir = Path(f"{settings.STORAGE_DIR}/{user_id}/{case_name}")
    case_dir.mkdir(parents=True, exist_ok=True)

    file_names = []
    for uploaded_file in files:
        file_path = os.path.join(case_dir, uploaded_file.filename)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.file.read())
        file_names.append(uploaded_file.filename)

    case_info = CaseInfo(
        name=case_name,
        unique_name=f"{user_id}_{case_name}",
        status="processing",
        number_of_PDFs=len(files),
        files=file_names,
        case_dir=case_dir,
    )
    case_info.save()


    background_tasks.add_task(process_case, case_info=case_info)

    end_time = time.time()
    logger.info(f"done create_new_case, total time {end_time - start_time}")

    return case_info


@app.get("/get_cases")
def get_cases(user_id: str):
    logger.info("start get_cases")
    start_time = time.time()

    """
    Return a list of all previously uploaded cases for a specific user with their metadata.
    """
    user_storage_dir = os.path.join(settings.STORAGE_DIR, user_id)
    if not os.path.exists(user_storage_dir):
        return {"message": "No cases found.", "cases": []}

    cases = os.listdir(user_storage_dir)
    case_data = []

    for case in cases:
        case_info_path = os.path.join(user_storage_dir, case, settings.CASE_INFO_FILENAME)
        if os.path.exists(case_info_path):
            with open(case_info_path, "r") as json_file:
                case_info = CaseInfo(**json.load(json_file))
                case_data.append(case_info.dict())

    # Add common cases
    common_cases_dir = os.path.join(settings.STORAGE_DIR, "common_cases")
    if os.path.exists(common_cases_dir):
        common_cases = os.listdir(common_cases_dir)
        for case in common_cases:
            case_info_path = os.path.join(common_cases_dir, case, settings.CASE_INFO_FILENAME)
            if os.path.exists(case_info_path):
                with open(case_info_path, "r") as json_file:
                    case_info = CaseInfo(**json.load(json_file))
                    case_data.append(case_info.dict())

    if not case_data:
        return {"message": "No case data found.", "cases": []}

    end_time = time.time()
    logger.info(f"done get_cases, total time {end_time - start_time}")

    return {"cases": case_data}


@app.get("/get_case/{case_name}")
def get_case(user_id: str, case_name: str) -> CaseInfo:
    logger.info("start get_case")
    start_time = time.time()

    """
    Return the metadata of a specific case by its name for a specific user.
    """
    case_info_path = os.path.join(settings.STORAGE_DIR, user_id, case_name, settings.CASE_INFO_FILENAME)
    if not os.path.exists(case_info_path):
        # Check common cases
        case_info_path = os.path.join(settings.STORAGE_DIR, "common_cases", case_name, settings.CASE_INFO_FILENAME)
        if not os.path.exists(case_info_path):
            raise HTTPException(status_code=404, detail="Case info not found.")

    with open(case_info_path, "r") as json_file:
        case_info = CaseInfo(**json.load(json_file))

    end_time = time.time()
    logger.info(f"done get_case, total time {end_time - start_time}")

    return case_info.dict()

@app.delete("/delete_case/{case_name}")
def delete_case(user_id: str, case_name: str):
    logger.info("start delete_case")
    start_time = time.time()

    """
    Delete a specific case for a specific user.
    """
    # Delete the case from storage
    case_dir = os.path.join(settings.STORAGE_DIR, user_id, case_name)
    if os.path.exists(case_dir):
        shutil.rmtree(case_dir)
    else:
        raise HTTPException(status_code=404, detail="Case not found in storage.")

    # Delete the case from Qdrant
    try:
        ingest_client.qdrant_client.delete_collection(case_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while deleting the case from Qdrant: {str(e)}")

    end_time = time.time()
    logger.info(f"done delete_case, total time {end_time - start_time}")

    return {"message": f"Case '{case_name}' has been deleted."}


@app.get("/health")
def health_check():
    return {"status": "ok"}
