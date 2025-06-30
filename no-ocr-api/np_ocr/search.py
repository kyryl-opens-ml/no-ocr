import base64
import io
import json
import logging
import time
from io import BytesIO
from pathlib import Path
from typing import List

import lancedb
import numpy as np
import PIL
import pyarrow as pa
import requests
from openai import OpenAI
from pydantic import BaseModel
from tqdm import tqdm

logger = logging.getLogger()

class ImageAnswer(BaseModel):
    answer: str

class CaseInfo(BaseModel):
    name: str
    unique_name: str
    status: str
    number_of_pdfs: int
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

class SearchClient:
    def __init__(self, storage_dir: str, vector_size: int,  base_url: str, token: str):
        self.storage_dir = storage_dir
        self.vector_size = vector_size
        self.colpali_client = ColPaliClient(base_url, token)

    def ingest(self, case_name: str, dataset, user_id: str, batch_size: int = 50):
        """Ingest a dataset of images into LanceDB in batches."""
        logger.info("start ingest")
        start_time = time.time()

        schema = pa.schema(
            [
                pa.field("index", pa.int64()),
                pa.field("pdf_name", pa.string()),
                pa.field("pdf_page", pa.int64()),
                pa.field("vector", pa.list_(pa.list_(pa.float32(), self.vector_size))),
            ]
        )
        lance_client = lancedb.connect(f"{self.storage_dir}/{user_id}/{case_name}")
        tbl = lance_client.create_table(case_name, schema=schema)

        with tqdm(total=len(dataset), desc="Indexing Progress") as pbar:
            batch = []
            for i in range(len(dataset)):
                image = dataset[i]["image"]
                response = self.colpali_client.process_pil_image(image)
                image_embedding = response["embedding"]

                batch.append(
                    {
                        "index": dataset[i]["index"],
                        "pdf_name": dataset[i]["pdf_name"],
                        "pdf_page": dataset[i]["pdf_page"],
                        "vector": image_embedding,
                    }
                )

                if len(batch) >= batch_size:
                    try:
                        tbl.add(batch)
                    except Exception as e:
                        logger.error(f"Error during upsert: {e}")
                    batch = []
                pbar.update(1)

            if batch:
                try:
                    tbl.add(batch)
                except Exception as e:
                    logger.error(f"Error during upsert: {e}")

        tbl.create_index(metric="cosine")

        logger.info("Indexing complete!")
        end_time = time.time()
        logger.info(f"done ingest, total time {end_time - start_time}")

    def search_images_by_text(self, query_text, case_name: str, user_id: str,top_k: int):
        logger.info("start search_images_by_text")
        start_time = time.time()

        lance_client = lancedb.connect(f"{self.storage_dir}/{user_id}/{case_name}")
        tbl = lance_client.open_table(case_name)

        query_embedding = self.colpali_client.query_text(query_text)
        multivector_query = np.array(query_embedding["embedding"])
        search_result = tbl.search(multivector_query).limit(top_k).select(["index", "pdf_name", "pdf_page"]).to_list()

        end_time = time.time()
        logger.info(f"done search_images_by_text, total time {end_time - start_time}")

        return search_result


def call_vllm(image_data: PIL.Image.Image, user_query: str, base_url: str, api_key: str, model: str) -> ImageAnswer:
    logger.info("start call_vllm")
    start_time = time.time()


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
