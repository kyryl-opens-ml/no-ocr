# Vision Retrieval

## Presentation

https://docs.google.com/presentation/d/1LY3KxUjuLAoCvKh9UyXtQupqiSTi_BFNUQ_Cdl6-o_g/edit#slide=id.g2f6ce2a35cc_0_103


## TLDR

![alt text](./docs/tldr.png)

## Setup

```
pip install modal
modal setup
```

## Run 

```
modal run vision_retrieval/infra.py
```

## Deploy 


```
modal deploy vision_retrieval/infra.py
```

## Develop

```
modal shell vision_retrieval/infra.py
```

## Orchestrate


```
pip install dagster dagster-webserver -U
dagster dev -f vision_retrieval/pipeline.py -p 3000 -h 0.0.0.0
```



## References

- [ColPali](https://arxiv.org/abs/2407.01449)
- [LanceDB](https://lancedb.com/)
- [ModalLab](https://modal.com/)
- [Dagster](https://dagster.io/)
- [Beyond Text: The Rise of Vision-Driven Document Retrieval for RAG](https://blog.vespa.ai/the-rise-of-vision-driven-document-retrieval-for-rag/)
- [PDF Retrieval with Vision Language Models](https://blog.vespa.ai/retrieval-with-vision-language-models-colpali/)


## CREATE


curl -X 'POST' \
  'http://0.0.0.0:8000/create_collection' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'files=@wordpress-pdf-invoice-plugin-sample.pdf;type=application/pdf' \
  -F 'collection_name=invoice'


  "message": "Uploaded 1 PDFs to collection 'invoice'",
  "collection_info": {
    "name": "invoice",
    "status": "done",
    "number_of_PDFs": 1,
    "files": [
      "wordpress-pdf-invoice-plugin-sample.pdf"
    ]
  }
}

## GET 

curl -X 'GET' \
  'http://0.0.0.0:8000/get_collections' \
  -H 'accept: application/json'


{
  "collections": [
    {
      "name": "qwe",
      "status": "error",
      "number_of_PDFs": 1,
      "files": [
        "Invoice_21_2024-12-13.pdf"
      ]
    },
    {
      "name": "string",
      "status": "processing",
      "number_of_PDFs": 1,
      "files": [
        "Invoice_21_2024-12-13.pdf"
      ]
    },
    {
      "name": "123",
      "status": "error",
      "number_of_PDFs": 1,
      "files": [
        "Invoice_21_2024-12-13.pdf"
      ]
    },
    {
      "name": "asdf",
      "status": "done",
      "number_of_PDFs": 1,
      "files": [
        "Bank Account Details - RBC Online Banking.pdf"
      ]
    },
    {
      "name": "test",
      "status": "error",
      "number_of_PDFs": 1,
      "files": [
        "Georgian Alignment Fund I - LP Letter - Q3 _24 vF.pdf"
      ]
    },
    {
      "name": "invoice",
      "status": "done",
      "number_of_PDFs": 1,
      "files": [
        "wordpress-pdf-invoice-plugin-sample.pdf"
      ]
    }
  ]
}  


## SEARCH


curl -X 'POST' \
  'http://0.0.0.0:8000/search' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'user_query=test&collection_name=invoice'

{
  "search_results": [
    {
      "score": 7.3453054,
      "pdf_name": "wordpress-pdf-invoice-plugin-sample.pdf",
      "pdf_page": 1,
      "llm_interpretation": "I am sorry, I can't find enough relevant information on these pages to answer your question."
    }
  ]
}  


docker run -p 6333:6333 qdrant/qdrant:v1.12.5
fastapi dev api.py
npm run dev