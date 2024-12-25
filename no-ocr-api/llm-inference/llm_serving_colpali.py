import modal

vllm_image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("vllm==0.6.3post1", "fastapi[standard]==0.115.4")
    .pip_install("colpali-engine")
)

MODELS_DIR = "/models"
MODEL_NAME = "vidore/colqwen2-v1.0-merged"


try:
    volume = modal.Volume.lookup("models", create_if_missing=False)
except modal.exception.NotFoundError:
    raise Exception("Download models first with modal run download_llama.py")


app = modal.App("colpali-embedding")

N_GPU = 1
TOKEN = "super-secret-token"

MINUTES = 60  # seconds
HOURS = 60 * MINUTES


@app.function(
    image=vllm_image,
    gpu=modal.gpu.A100(count=N_GPU),
    keep_warm=0,
    container_idle_timeout=1 * MINUTES,
    timeout=24 * HOURS,
    allow_concurrent_inputs=1000,
    volumes={MODELS_DIR: volume},
)
@modal.asgi_app()
def serve():
    import fastapi
    import torch
    from colpali_engine.models import ColQwen2, ColQwen2Processor
    from fastapi import APIRouter, Depends, HTTPException, Security
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.security import HTTPBearer

    volume.reload()  # ensure we have the latest version of the weights

    # create a fastAPI app for serving the ColPali model
    web_app = fastapi.FastAPI(
        title=f"ColPali {MODEL_NAME} server",
        description="Run a ColPali model server with fastAPI on modal.com 🚀",
        version="0.0.1",
        docs_url="/docs",
    )

    # security: CORS middleware for external requests
    http_bearer = HTTPBearer(
        scheme_name="Bearer Token",
        description="See code for authentication details.",
    )
    web_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # security: inject dependency on authed routes
    async def is_authenticated(api_key: str = Security(http_bearer)):
        if api_key.credentials != TOKEN:
            raise HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return {"username": "authenticated_user"}

    router = APIRouter(dependencies=[Depends(is_authenticated)])

    # Define the model and processor
    model_name = "/models/vidore/colqwen2-v1.0-merged"
    colpali_model = ColQwen2.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="cuda:0",
    ).eval()

    colpali_processor = ColQwen2Processor.from_pretrained(model_name)

    # Define a simple endpoint to process text queries
    @router.post("/query")
    async def query_model(query_text: str):
        with torch.no_grad():
            batch_query = colpali_processor.process_queries([query_text]).to(colpali_model.device)
            query_embedding = colpali_model(**batch_query)
        return {"embedding": query_embedding[0].cpu().float().numpy().tolist()}

    @router.post("/process_image")
    async def process_image(image: fastapi.UploadFile):
        from PIL import Image

        pil_image = Image.open(image.file)
        with torch.no_grad():
            batch_image = colpali_processor.process_images([pil_image]).to(colpali_model.device)
            image_embedding = colpali_model(**batch_image)
        return {"embedding": image_embedding[0].cpu().float().numpy().tolist()}

    # add authed router to our fastAPI app
    web_app.include_router(router)

    return web_app
