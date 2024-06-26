from fastapi import FastAPI
from fastapi import (
    HTTPException,
    status,
    Depends,
)
from fastapi.middleware.cors import CORSMiddleware
from openai.types.beta import VectorStore
from openai.types.beta.vector_store import FileCounts
from openai.types.beta.vector_store_deleted import VectorStoreDeleted
from pydantic import BaseModel

from utils.pipelines.auth import get_current_user

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateVectorStoreForm(BaseModel):
    file_ids: list[str] | None
    name: str | None
    metadata: dict | None


class ModifyVectorStoreForm(BaseModel):
    name: str | None
    metadata: dict | None


@app.post("/")
async def create_vector_store(form_data: CreateVectorStoreForm,
                              user: str = Depends(get_current_user)):
    try:
        return VectorStore(
            id="store-123",
            created_at=561651,
            file_counts=FileCounts(cancelled=1, completed=1, failed=1, in_progress=1, total=1),
            name=form_data.name,
            object="vector_store",
            status="completed",
            usage_bytes=123,
            metadata=form_data.metadata,
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(e)}"
        )


@app.delete("/{vector_store_id}")
async def delete_vector_store(vector_store_id: str,
                              user: str = Depends(get_current_user)):
    try:
        return VectorStoreDeleted(
            id=vector_store_id,
            deleted=True,
            object="vector_store.deleted",
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(e)}",
        )


@app.get("/")
async def list_vector_stores(limit: int | None = None,
                             order: str | None = None,
                             after: str | None = None,
                             before: str | None = None,
                             user: str = Depends(get_current_user)):
    try:
        return {
            "object": "list",
            "data": [
                VectorStore(
                    id="store-123",
                    created_at=561651,
                    file_counts=FileCounts(cancelled=1, completed=1, failed=1, in_progress=1, total=1),
                    name="asdf",
                    object="vector_store",
                    status="completed",
                    usage_bytes=123,
                    metadata={},
                )
            ]
        }
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(e)}",
        )


@app.get("/{vector_store_id}")
async def retrieve_vector_store(vector_store_id: str,
                                user: str = Depends(get_current_user)):
    try:
        return VectorStore(
            id=vector_store_id,
            created_at=561651,
            file_counts=FileCounts(cancelled=1, completed=1, failed=1, in_progress=1, total=1),
            name="asdf",
            object="vector_store",
            status="completed",
            usage_bytes=123,
            metadata={},
        )

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(e)}",
        )


@app.post("/{vector_store_id}")
async def modify_vector_store(vector_store_id: str,
                              form_data: ModifyVectorStoreForm,
                              user: str = Depends(get_current_user)):
    try:
        return VectorStore(
            id=vector_store_id,
            created_at=561651,
            file_counts=FileCounts(cancelled=1, completed=1, failed=1, in_progress=1, total=1),
            name=form_data.name,
            object="vector_store",
            status="completed",
            usage_bytes=123,
            metadata=form_data.metadata,
        )

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(e)}",
        )
