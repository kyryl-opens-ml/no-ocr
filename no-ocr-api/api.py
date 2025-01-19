from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import json
import os
from pathlib import Path
import PIL.Image
import pandas as pd
import base64
from io import BytesIO
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from datasets import load_from_disk
import PIL
from openai import OpenAI
import io
import tracemalloc
from pathlib import Path
import time

import requests
from datasets import Dataset
from pdf2image import convert_from_path
from pypdf import PdfReader
from qdrant_client import QdrantClient, models

from tqdm import tqdm
import shutil
import diskcache as dc
import logging


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



class ColPaliClient:
    def __init__(self, base_url: str = settings.COLPALI_BASE_URL, token: str = settings.COLPALI_TOKEN):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}

    def query_text(self, query_text: str):
        response = requests.post(f"{self.base_url}/query", headers=self.headers, params={"query_text": query_text})
        response.raise_for_status()
        return response.json()

    def process_image(self, image_path: str):
        with open(image_path, "rb") as image_file:
            files = {"image": image_file}
            response = requests.post(f"{self.base_url}/process_image", files=files, headers=self.headers)
            response.raise_for_status()
            return response.json()

    def process_pil_image(self, pil_image):
        buffered = io.BytesIO()
        pil_image.save(buffered, format="JPEG")
        files = {"image": buffered.getvalue()}
        response = requests.post(f"{self.base_url}/process_image", files=files, headers=self.headers)
        response.raise_for_status()
        return response.json()


class IngestClient:
    def __init__(self, qdrant_uri: str = settings.QDRANT_URI):
        self.qdrant_client = QdrantClient(qdrant_uri, port=settings.QDRANT_PORT, https=settings.QDRANT_HTTPS)
        self.colpali_client = ColPaliClient()

    def ingest(self, case_name, dataset):
        logger.info("start ingest")
        start_time = time.time()
        
        self.qdrant_client.create_collection(
            collection_name=case_name,
            on_disk_payload=True,
            optimizers_config=models.OptimizersConfigDiff(indexing_threshold=settings.INDEXING_THRESHOLD),
            vectors_config=models.VectorParams(
                size=settings.VECTOR_SIZE,
                distance=models.Distance.COSINE,
                multivector_config=models.MultiVectorConfig(comparator=models.MultiVectorComparator.MAX_SIM),
                quantization_config=models.ScalarQuantization(
                    scalar=models.ScalarQuantizationConfig(
                        type=models.ScalarType.INT8,
                        quantile=settings.QUANTILE,
                        always_ram=True,
                    ),
                ),
            ),
        )

        # Use tqdm to create a progress bar
        with tqdm(total=len(dataset), desc="Indexing Progress") as pbar:
            for i in range(len(dataset)):
                # The images are already PIL Image objects, so we can use them directly
                image = dataset[i]["image"]

                # Process and encode image using ColPaliClient
                response = self.colpali_client.process_pil_image(image)
                image_embedding = response["embedding"]

                # Prepare point for Qdrant
                point = models.PointStruct(
                    id=i,  # we just use the index as the ID
                    vector=image_embedding,  # This is now a list of vectors
                    payload={
                        "index": dataset[i]["index"],
                        "pdf_name": dataset[i]["pdf_name"],
                        "pdf_page": dataset[i]["pdf_page"],
                    },  # can also add other metadata/data
                )

                try:
                    self.qdrant_client.upsert(
                        collection_name=case_name,
                        points=[point],
                        wait=False,
                    )
                except Exception as e:
                    logger.error(f"Error during upsert: {e}")
                    continue
                pbar.update(1)

        logger.info("Indexing complete!")
        end_time = time.time()
        logger.info(f"done ingest, total time {end_time - start_time}")


class SearchClient:
    def __init__(self, qdrant_uri: str = settings.QDRANT_URI):
        self.qdrant_client = QdrantClient(qdrant_uri, port=settings.QDRANT_PORT, https=settings.QDRANT_HTTPS)
        self.colpali_client = ColPaliClient()

    def search_images_by_text(self, query_text, case_name: str, top_k=settings.TOP_K):
        logger.info("start search_images_by_text")
        start_time = time.time()
        
        # Use ColPaliClient to query text and get the embedding
        query_embedding = self.colpali_client.query_text(query_text)

        # Extract the embedding from the response
        multivector_query = query_embedding["embedding"]

        # Search in Qdrant
        search_result = self.qdrant_client.query_points(collection_name=case_name, query=multivector_query, limit=top_k)
        
        end_time = time.time()
        logger.info(f"done search_images_by_text, total time {end_time - start_time}")

        return search_result


def get_pdf_images(pdf_path):
    logger.info("start get_pdf_images")
    start_time = time.time()
    
    reader = PdfReader(pdf_path)
    page_texts = []
    for page_number in range(len(reader.pages)):
        page = reader.pages[page_number]
        text = page.extract_text()
        page_texts.append(text)
    # Convert to PIL images
    images = convert_from_path(
        pdf_path, dpi=150, fmt="jpeg", jpegopt={"quality": 100, "progressive": True, "optimize": True}
    )
    assert len(images) == len(page_texts)
    
    end_time = time.time()
    logger.info(f"done get_pdf_images, total time {end_time - start_time}")
    
    return images, page_texts


def pdfs_to_hf_dataset(path_to_folder):
    logger.info("start pdfs_to_hf_dataset")
    start_time = time.time()
    
    tracemalloc.start()  # Start tracing memory allocations

    data = []
    global_index = 0

    folder_path = Path(path_to_folder)
    pdf_files = list(folder_path.glob("*.pdf"))
    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        images, page_texts = get_pdf_images(str(pdf_file))

        for page_number, (image, text) in enumerate(zip(images, page_texts)):
            data.append(
                {
                    "image": image,
                    "index": global_index,
                    "pdf_name": pdf_file.name,
                    "pdf_page": page_number + 1,
                    "page_text": text,
                }
            )
            global_index += 1
            # Print memory usage after processing each image
            current, peak = tracemalloc.get_traced_memory()

        # Print memory usage after processing each PDF
        current, peak = tracemalloc.get_traced_memory()
        logger.info(f"PDF: Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")

    current, peak = tracemalloc.get_traced_memory()
    logger.info(f"TOTAL: Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")
    tracemalloc.stop()  # Stop tracing memory allocations

    logger.info("Done processing")
    dataset = Dataset.from_list(data)
    logger.info("Done converting to dataset")
    
    end_time = time.time()
    logger.info(f"done pdfs_to_hf_dataset, total time {end_time - start_time}")
    
    return dataset


def call_vllm(image_data: PIL.Image.Image, user_query: str) -> ImageAnswer:
    logger.info("start call_vllm")
    start_time = time.time()
    
    model = "Qwen2-VL-7B-Instruct"

    prompt = f"""
    Based on the user's query: 
    ###
    {user_query} 
    ###

    and the provided image, determine if the image contains enough information to answer the query.
    If it does, provide the most accurate answer possible based on the image.
    If it does not, respond with the exact phrase "NA".

    Please return your response in valid JSON with the structure:
    {{
        "answer": "Answer text or NA"
    }}
    """

    buffered = BytesIO()
    max_size = (512, 512)
    image_data.thumbnail(max_size)
    image_data.save(buffered, format="JPEG")
    img_b64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    client = OpenAI(base_url=settings.VLLM_URL, api_key=settings.COLPALI_TOKEN)
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_b64_str}"},
                    },
                ],
            }
        ],
        response_format=ImageAnswer,
        extra_body=dict(guided_decoding_backend="outlines"),
    )
    message = completion.choices[0].message
    result = message.parsed
    
    end_time = time.time()
    logger.info(f"done call_vllm, total time {end_time - start_time}")
    
    return result


search_client = SearchClient()
ingest_client = IngestClient()

cache = dc.Cache("vllm_cache")


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
    cache_key = f"{user_id}_{case_name}_{pdf_name}_{pdf_page}_{user_query}"
    if cache_key in cache:
        return cache[cache_key]

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

    image_answer = call_vllm(image_data, user_query)
    cache[cache_key] = image_answer
    
    end_time = time.time()
    logger.info(f"done vllm_call, total time {end_time - start_time}")
    
    return image_answer


@app.post("/search")
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

        search_results_data.append(
            {
                "score": score,
                "pdf_name": pdf_name,
                "pdf_page": pdf_page,
                "image_base64": img_b64_str,  # Add image data to the response
            }
        )
    
    end_time = time.time()
    logger.info(f"done ai_search, total time {end_time - start_time}")

    return {"search_results": search_results_data}


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


@app.delete("/delete_all_cases")
def delete_all_cases():
    logger.info("start delete_all_cases")
    start_time = time.time()
    
    """
    Delete all cases from storage and Qdrant.
    """
    # Delete all cases from storage
    if os.path.exists(settings.STORAGE_DIR):
        for case in os.listdir(settings.STORAGE_DIR):
            shutil.rmtree(os.path.join(settings.STORAGE_DIR, case))

    # Delete all cases from Qdrant
    cases = ingest_client.qdrant_client.get_collections().collections
    for case in cases:
        ingest_client.qdrant_client.delete_collection(case.name)
    
    end_time = time.time()
    logger.info(f"done delete_all_cases, total time {end_time - start_time}")

    return {"message": "All cases have been deleted from storage and Qdrant."}


@app.delete("/delete_case/{case_name}")
def delete_case(user_id: str, case_name: str):
    logger.info("start delete_case")
    start_time = time.time()
    
    """
    Delete a specific case from storage and Qdrant for a specific user.
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

    return {"message": f"Case '{case_name}' has been deleted from storage and Qdrant."}
