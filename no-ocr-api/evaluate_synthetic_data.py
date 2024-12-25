import base64
import os
import random
from io import BytesIO
from typing import Dict, List

import PIL
import typer
from colpali_engine.trainer.eval_utils import CustomRetrievalEvaluator
from datasets import Dataset, load_dataset
from openai import OpenAI
from pydantic import BaseModel
from rich import print
from rich.table import Table
from tqdm import tqdm

from ai_search_demo.qdrant_inexing import SearchClient, pdfs_to_hf_dataset, IngestClient

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class DataSample(BaseModel):
    japanese_query: str
    english_query: str

def generate_synthetic_question(image: PIL.Image.Image) -> DataSample:
    # Convert PIL image to base64 string
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    prompt = """
    I am developing a visual retrieval dataset to evaluate my system. 
    Based on the image I provided, I want you to generate a query that this image will satisfy. 
    For example, if a user types this query into the search box, this image would be extremely relevant.
    Generate the query in Japanese and English.
    """
    # Generate synthetic question using OpenAI
    chat_completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        response_format=DataSample,
        temperature=1,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            }
        ],
    )

    sample = chat_completion.choices[0].message.parsed
    return sample

def create_synthetic_dataset(input_folder: str, output_folder: str, hub_repo: str, num_samples: int = 10) -> None:
    # Step 1: Read all PDFs and extract info
    dataset = pdfs_to_hf_dataset(input_folder)

    # Step 2: Randomly sample data points
    if num_samples > len(dataset):
        indices = random.choices(range(len(dataset)), k=num_samples)
        sampled_data = dataset.select(indices)
    else:
        sampled_data = dataset.shuffle().select(range(num_samples))

    synthetic_data: List[Dict] = []

    for index, data_point in enumerate(tqdm(sampled_data, desc="Generating synthetic questions")):
        image = data_point['image']
        pdf_name = data_point['pdf_name']
        pdf_page = data_point['pdf_page']

        # Step 3: Generate synthetic question
        sample = generate_synthetic_question(image)

        # Step 4: Store samples in a new dataset
        synthetic_data.append({
            "index": index,
            "image": image,
            "question_en": sample.english_query,
            "question_jp": sample.japanese_query,
            "pdf_name": pdf_name,
            "pdf_page": pdf_page
        })

    # Create a new dataset from synthetic data
    synthetic_dataset = Dataset.from_list(synthetic_data)
    synthetic_dataset.save_to_disk(output_folder)

    # Save the dataset card
    synthetic_dataset.push_to_hub(hub_repo, private=False)

def evaluate_on_synthetic_dataset(hub_repo: str, collection_name: str = "synthetic-dataset-evaluate-full") -> None:
    # Ingest collection with IngestClient
    print("Load data")
    synthetic_dataset = load_dataset(hub_repo)['train']

    print("Ingest data to qdrant")
    # ingest_client = IngestClient()
    # ingest_client.ingest(collection_name, synthetic_dataset)

    run_evaluation(synthetic_dataset=synthetic_dataset, collection_name=collection_name, query_text_key='question_en')
    run_evaluation(synthetic_dataset=synthetic_dataset, collection_name=collection_name, query_text_key='question_jp')

def run_evaluation(synthetic_dataset: Dataset, collection_name: str, query_text_key: str) -> None:
    search_client = SearchClient()
    relevant_docs: Dict[str, Dict[str, int]] = {}
    results: Dict[str, Dict[str, float]] = {}

    for x in synthetic_dataset:
        query_id = f"{x['pdf_name']}_{x['pdf_page']}"
        relevant_docs[query_id] = {query_id: 1}  # The most relevant document is itself

        response = search_client.search_images_by_text(query_text=x[query_text_key], collection_name=collection_name, top_k=10)
        
        results[query_id] = {}
        for point in response.points:
            doc_id = f"{point.payload['pdf_name']}_{point.payload['pdf_page']}"
            results[query_id][doc_id] = point.score

    mteb_evaluator = CustomRetrievalEvaluator()

    ndcg, _map, recall, precision, naucs = mteb_evaluator.evaluate(
        relevant_docs,
        results,
        mteb_evaluator.k_values,
    )

    mrr = mteb_evaluator.evaluate_custom(relevant_docs, results, mteb_evaluator.k_values, "mrr")

    scores = {
        **{f"ndcg_at_{k.split('@')[1]}": v for (k, v) in ndcg.items()},
        **{f"map_at_{k.split('@')[1]}": v for (k, v) in _map.items()},
        **{f"recall_at_{k.split('@')[1]}": v for (k, v) in recall.items()},
        **{f"precision_at_{k.split('@')[1]}": v for (k, v) in precision.items()},
        **{f"mrr_at_{k.split('@')[1]}": v for (k, v) in mrr[0].items()},
        **{f"naucs_at_{k.split('@')[1]}": v for (k, v) in naucs.items()},
    }

    # Use rich to print scores beautifully
    table = Table(title=f"Evaluation Scores for {query_text_key}")
    table.add_column("Metric", justify="right", style="cyan", no_wrap=True)
    table.add_column("Score", style="magenta")

    for metric, score in scores.items():
        table.add_row(metric, f"{score:.4f}")

    print(table)


if __name__ == '__main__':
    app = typer.Typer()
    app.command()(create_synthetic_dataset)
    app.command()(evaluate_on_synthetic_dataset)
    app()