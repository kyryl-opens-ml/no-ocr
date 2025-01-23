import base64
import io
import json
import logging
import time
from io import BytesIO
from pathlib import Path
from typing import List

import PIL
import requests
from openai import OpenAI
from pydantic import BaseModel
from qdrant_client import QdrantClient, models
from tqdm import tqdm

logger = logging.getLogger()

class ImageAnswer(BaseModel):
    answer: str

class CaseInfo(BaseModel):
    name: str
    unique_name: str
    status: str
    number_of_PDFs: int
    files: List[str]
    case_dir: Path

    def save(self, case_info_filename: str):
        with open(self.case_dir / case_info_filename, "w") as json_file:
            json.dump(self.model_dump(), json_file, default=str)

    def update_status(self, new_status: str, case_info_filename: str):
        self.status = new_status
        self.save(case_info_filename)



class ColPaliClient:
    def __init__(self, base_url: str, token: str):
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
    def __init__(self, qdrant_uri: str, port: int, https: bool, index_threshold: int, vector_size: int, quantile: float, top_k: int, base_url: str, token: str):
        self.qdrant_client = QdrantClient(qdrant_uri, port=port, https=https)
        self.colpali_client = ColPaliClient(base_url, token)
        self.index_threshold = index_threshold
        self.vector_size = vector_size
        self.quantile = quantile
        self.top_k = top_k

    def ingest(self, case_name, dataset):
        logger.info("start ingest")
        start_time = time.time()

        self.qdrant_client.create_collection(
            collection_name=case_name,
            on_disk_payload=True,
            optimizers_config=models.OptimizersConfigDiff(indexing_threshold=self.index_threshold),
            vectors_config=models.VectorParams(
                size=self.vector_size,
                distance=models.Distance.COSINE,
                multivector_config=models.MultiVectorConfig(comparator=models.MultiVectorComparator.MAX_SIM),
                quantization_config=models.ScalarQuantization(
                    scalar=models.ScalarQuantizationConfig(
                        type=models.ScalarType.INT8,
                        quantile=self.quantile,
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
    def __init__(self, qdrant_uri: str, port: int, https: bool, top_k: int, base_url: str, token: str):
        self.qdrant_client = QdrantClient(qdrant_uri, port=port, https=https)
        self.colpali_client = ColPaliClient(base_url=base_url, token=token)
        self.top_k = top_k

    def search_images_by_text(self, query_text, case_name: str, top_k: int):
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



def call_vllm(image_data: PIL.Image.Image, user_query: str, base_url: str, api_key: str, model: str) -> ImageAnswer:
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

    print(prompt)
    buffered = BytesIO()
    max_size = (512, 512)
    image_data.thumbnail(max_size)
    image_data.save(buffered, format="JPEG")
    img_b64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    client = OpenAI(base_url=base_url, api_key=api_key)
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
