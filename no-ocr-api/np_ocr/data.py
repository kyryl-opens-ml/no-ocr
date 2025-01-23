import logging
import time
import tracemalloc
from pathlib import Path

from datasets import Dataset
from pdf2image import convert_from_path
from pypdf import PdfReader
from tqdm import tqdm

logger = logging.getLogger()


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
