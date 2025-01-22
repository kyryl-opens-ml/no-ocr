from fastapi import FastAPI, APIRouter, HTTPException, Security, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import numpy as np

app = FastAPI(
    title="Mock ColPali Server",
    description="Mock server for ColPali model with FastAPI",
    version="0.0.1",
    docs_url="/docs",
)

# Security: CORS middleware for external requests
http_bearer = HTTPBearer(
    scheme_name="Bearer Token",
    description="See code for authentication details.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security: inject dependency on authed routes
TOKEN = "super-secret-token"

async def is_authenticated(api_key: str = Security(http_bearer)):
    if api_key.credentials != TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        )
    return {"username": "authenticated_user"}

router = APIRouter(dependencies=[Depends(is_authenticated)])

# Define a simple endpoint to process text queries
@router.post("/query")
async def query_model(query_text: str):
    # Mock response: generate a random embedding with shape (3, 128)
    mock_embedding = np.random.rand(3, 128).tolist()
    return {"embedding": mock_embedding}

@router.post("/process_image")
async def process_image(image: UploadFile):
    # Mock response: generate a random embedding with shape (1030, 128)
    mock_embedding = np.random.rand(1030, 128).tolist()
    return {"embedding": mock_embedding}

# Add authed router to our FastAPI app
app.include_router(router)