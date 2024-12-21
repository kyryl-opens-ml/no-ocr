from fastapi import FastAPI, UploadFile, File, Form, HTTPException
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

import requests
from datasets import Dataset
from pdf2image import convert_from_path
from pypdf import PdfReader
from qdrant_client import QdrantClient, models

from tqdm import tqdm

app = FastAPI()

# Add CORS middleware to allow any application to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class Settings(BaseSettings):
    STORAGE_DIR: str = "storage"
    COLLECTION_INFO_FILENAME: str = "collection_info.json"
    HF_DATASET_DIRNAME: str = "hf_dataset"
    README_FILENAME: str = "README.md"
    SEARCH_TOP_K: int = 5
    COLPALI_TOKEN: str = "super-secret-token"
    VLLM_URL: str = "https://truskovskiyk--qwen2-vllm-serve.modal.run/v1/"
    COLPALI_BASE_URL: str = "https://truskovskiyk--colpali-embedding-serve.modal.run"
    QDRANT_URI: str = "https://no-orc-qdrant.up.railway.app"
    QDRANT_PORT: int = 443
    VECTOR_SIZE: int = 128
    INDEXING_THRESHOLD: int = 100
    QUANTILE: float = 0.99
    TOP_K: int = 5
    
    class Config:
        env_file = ".env"

settings = Settings()






class ColPaliClient:
    def __init__(self, base_url: str = settings.COLPALI_BASE_URL, token: str = settings.COLPALI_TOKEN):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}

    def query_text(self, query_text: str):
        response = requests.post(
            f"{self.base_url}/query",
            headers=self.headers,
            params={"query_text": query_text}
        )
        response.raise_for_status()
        return response.json()

    def process_image(self, image_path: str):
        with open(image_path, "rb") as image_file:
            files = {"image": image_file}
            response = requests.post(
                f"{self.base_url}/process_image",
                files=files,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    def process_pil_image(self, pil_image):
        buffered = io.BytesIO()
        pil_image.save(buffered, format="JPEG")
        files = {"image": buffered.getvalue()}
        response = requests.post(
            f"{self.base_url}/process_image",
            files=files,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
        

class IngestClient:
    def __init__(self, qdrant_uri: str = settings.QDRANT_URI):
        self.qdrant_client = QdrantClient(qdrant_uri, port=settings.QDRANT_PORT, https=True)
        self.colpali_client = ColPaliClient()

    def ingest(self, collection_name, dataset):
        self.qdrant_client.create_collection(
            collection_name=collection_name,
            on_disk_payload=True,
            optimizers_config=models.OptimizersConfigDiff(
                indexing_threshold=settings.INDEXING_THRESHOLD
            ),
            vectors_config=models.VectorParams(
                size=settings.VECTOR_SIZE,
                distance=models.Distance.COSINE,
                multivector_config=models.MultiVectorConfig(
                    comparator=models.MultiVectorComparator.MAX_SIM
                ),
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
                image_embedding = response['embedding']

                # Prepare point for Qdrant
                point = models.PointStruct(
                    id=i,  # we just use the index as the ID
                    vector=image_embedding,  # This is now a list of vectors
                    payload={
                        "index": dataset[i]['index'],
                        "pdf_name": dataset[i]['pdf_name'],
                        "pdf_page": dataset[i]['pdf_page'],
                    },  # can also add other metadata/data
                )

                # Upload point to Qdrant
                try:
                    self.qdrant_client.upsert(
                        collection_name=collection_name,
                        points=[point],
                        wait=False,
                    )                    
                # clown level error handling here 🤡
                except Exception as e:
                    print(f"Error during upsert: {e}")
                    continue

                # Update the progress bar
                pbar.update(1)

        print("Indexing complete!")           

class SearchClient:
    def __init__(self, qdrant_uri: str = settings.QDRANT_URI):
        self.qdrant_client = QdrantClient(qdrant_uri, port=settings.QDRANT_PORT, https=True)
        self.colpali_client = ColPaliClient()

    def search_images_by_text(self, query_text, collection_name: str, top_k=settings.TOP_K):
        # Use ColPaliClient to query text and get the embedding
        query_embedding = self.colpali_client.query_text(query_text)

        # Extract the embedding from the response
        multivector_query = query_embedding['embedding']

        # Search in Qdrant
        search_result = self.qdrant_client.query_points(
            collection_name=collection_name, query=multivector_query, limit=top_k
        )

        return search_result



def get_pdf_images(pdf_path):
    reader = PdfReader(pdf_path)
    page_texts = []
    for page_number in range(len(reader.pages)):
        page = reader.pages[page_number]
        text = page.extract_text()
        page_texts.append(text)
    # Convert to PIL images
    images = convert_from_path(pdf_path, dpi=150, fmt="jpeg", jpegopt={"quality": 100, "progressive": True, "optimize": True})
    assert len(images) == len(page_texts)
    return images, page_texts

def pdfs_to_hf_dataset(path_to_folder):
    tracemalloc.start()  # Start tracing memory allocations

    data = []
    global_index = 0

    folder_path = Path(path_to_folder)
    pdf_files = list(folder_path.glob("*.pdf"))
    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        images, page_texts = get_pdf_images(str(pdf_file))

        for page_number, (image, text) in enumerate(zip(images, page_texts)):
            data.append({
                "image": image,
                "index": global_index,
                "pdf_name": pdf_file.name,
                "pdf_page": page_number + 1,
                "page_text": text
            })
            global_index += 1
            # Print memory usage after processing each image
            current, peak = tracemalloc.get_traced_memory()

        # Print memory usage after processing each PDF
        current, peak = tracemalloc.get_traced_memory()
        print(f"PDF: Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")

    current, peak = tracemalloc.get_traced_memory()
    print(f"TOTAL: Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")
    tracemalloc.stop()  # Stop tracing memory allocations

    print("Done processing")
    dataset = Dataset.from_list(data)
    print("Done converting to dataset")
    return dataset


def call_vllm(image_data: PIL.Image.Image):
    """
    Send image data to the Qwen2-VL-7B-Instruct endpoint and get the response.

    If no answer can be found from the image for the user's query, 
    a default message is returned.
    """
    model = "Qwen2-VL-7B-Instruct"
    prompt = """
    If the user query is a question, try your best to answer it based on the provided images. 
    If the user query can not be interpreted as a question, or if the answer to the query can not be inferred from the images,
    answer with the exact phrase "I am sorry, I can't find enough relevant information on these pages to answer your question.".
    """

    buffered = BytesIO()
    max_size = (512, 512)
    image_data.thumbnail(max_size)
    image_data.save(buffered, format="JPEG")
    img_b64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    client = OpenAI(base_url=settings.VLLM_URL, api_key=settings.COLPALI_TOKEN)
    chat_completion = client.chat.completions.create(
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
    )
    return chat_completion.choices[0].message.content

search_client = SearchClient()
ingest_client = IngestClient()

@app.post("/search")
def ai_search(
    user_query: str = Form(...),
    collection_name: str = Form(...)
):
    """
    Given a user query and collection name, search relevant images in the Qdrant index
    and return both the results and an LLM interpretation.
    """
    if not os.path.exists(settings.STORAGE_DIR):
        raise HTTPException(status_code=404, detail="No collections found.")
    
    collection_info_path = os.path.join(settings.STORAGE_DIR, collection_name, settings.COLLECTION_INFO_FILENAME)
    if not os.path.exists(collection_info_path):
        raise HTTPException(status_code=404, detail="Collection info not found.")
    
    with open(collection_info_path, "r") as json_file:
        _ = json.load(json_file)  # collection_info is not used directly below

    search_results = search_client.search_images_by_text(
        user_query,
        collection_name=collection_name,
        top_k=settings.SEARCH_TOP_K
    )
    if not search_results:
        return {"message": "No results found."}

    # dataset_path = os.path.join(settings.STORAGE_DIR, collection_name, settings.HF_DATASET_DIRNAME)
    # if not os.path.exists(dataset_path):
    #     raise HTTPException(status_code=404, detail="Dataset for this collection not found.")

    # dataset = load_from_disk(dataset_path)
    search_results_data = []
    for result in search_results.points:
        payload = result.payload
        print(payload)
        score = result.score
        # image_data = dataset[payload['index']]['image']
        # pdf_name = dataset[payload['index']]['pdf_name']
        # pdf_page = dataset[payload['index']]['pdf_page']

        # Prepare LLM interpretation
        # image_obj = PIL.Image.fromarray(image_data) if not isinstance(image_data, PIL.Image.Image) else image_data
        # vllm_output = call_vllm(image_obj)
        pdf_name = 1
        pdf_page = 1
        vllm_output = "mock"
        search_results_data.append({
            "score": score,
            "pdf_name": pdf_name,
            "pdf_page": pdf_page,
            "llm_interpretation": vllm_output
        })

    return {"search_results": search_results_data}

@app.post("/create_collection")
def create_new_collection(
    files: List[UploadFile] = File(...),
    collection_name: str = Form(...)
):
    """
    Create a new collection, store the uploaded PDFs, and process/ingest them.
    """
    if not files or not collection_name:
        raise HTTPException(status_code=400, detail="No files or collection name provided.")
    
    collection_dir = f"{settings.STORAGE_DIR}/{collection_name}"
    os.makedirs(collection_dir, exist_ok=True)

    file_names = []
    for uploaded_file in files:
        file_path = os.path.join(collection_dir, uploaded_file.filename)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.file.read())
        file_names.append(uploaded_file.filename)

    collection_info = {
        "name": collection_name,
        "status": "processing",
        "number_of_PDFs": len(files),
        "files": file_names
    }
    with open(os.path.join(collection_dir, settings.COLLECTION_INFO_FILENAME), "w") as json_file:
        json.dump(collection_info, json_file)

    # Process and ingest
    try:
        dataset = pdfs_to_hf_dataset(collection_dir)
        dataset.save_to_disk(os.path.join(collection_dir, settings.HF_DATASET_DIRNAME))
        ingest_client.ingest(collection_name, dataset)
        collection_info['status'] = 'done'
    except Exception as e:
        collection_info['status'] = 'error'
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        with open(os.path.join(collection_dir, settings.COLLECTION_INFO_FILENAME), "w") as json_file:
            json.dump(collection_info, json_file)

    return {
        "message": f"Uploaded {len(files)} PDFs to collection '{collection_name}'",
        "collection_info": collection_info
    }

@app.get("/get_collections")
def get_collections():
    """
    Return a list of all previously uploaded collections with their metadata.
    """
    if not os.path.exists(settings.STORAGE_DIR):
        return {"message": "No collections found.", "collections": []}

    collections = os.listdir(settings.STORAGE_DIR)
    collection_data = []

    for collection in collections:
        collection_info_path = os.path.join(settings.STORAGE_DIR, collection, settings.COLLECTION_INFO_FILENAME)
        if os.path.exists(collection_info_path):
            with open(collection_info_path, "r") as json_file:
                collection_info = json.load(json_file)
                collection_data.append(collection_info)

    if not collection_data:
        return {"message": "No collection data found.", "collections": []}
    return {"collections": collection_data}
