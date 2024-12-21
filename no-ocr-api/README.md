# No OCR API

## Description

The No OCR API is a Python-based application designed to handle image processing tasks without relying on Optical Character Recognition (OCR). It provides a streamlined API for efficient image evaluation and manipulation.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd no-ocr-api
   ```

2. Build the Docker image:
   ```bash
   docker build -t no-ocr-api .
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the API:
   ```bash
   python api.py
   ```

2. Alternatively, run the API using Docker:
   ```bash
   docker run -p 8000:8000 no-ocr-api
   ```

3. Access the API at `http://localhost:8000`.
