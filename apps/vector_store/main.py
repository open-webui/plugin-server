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
from openai.types.beta.vector_stores import VectorStoreFile, VectorStoreFileDeleted
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


class StaticForm(BaseModel):
    max_chunk_size_tokens: int
    chunk_overlap_tokens: int


class AutoChunkingStrategyForm(BaseModel):
    type: str = "auto"


class StaticChunkingStrategyForm(BaseModel):
    type: str = "static"
    static: StaticForm


class CreateVectorStoreForm(BaseModel):
    file_ids: list[str] | None
    name: str | None
    chunking_strategy: StaticChunkingStrategyForm | AutoChunkingStrategyForm | None = None
    metadata: dict | None


class CreateVectorStoreFileForm(BaseModel):
    file_id: str
    chunking_strategy: StaticChunkingStrategyForm | AutoChunkingStrategyForm | None = None


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


@app.post("/{vector_store_id}/files")
async def create_vector_store_file(vector_store_id: str,
                                   form_data: CreateVectorStoreFileForm,
                                   user: str = Depends(get_current_user)):
    try:
        return VectorStoreFile(
            id="123",
            vector_store_id=vector_store_id,
            created_at=123456,
            object="vector_store.file",
            status="completed",
            usage_bytes=1234,
            chunking_strategy=form_data.chunking_strategy.model_dump()
        )

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(e)}",
        )


@app.delete("/{vector_store_id}/files/{file_id}")
async def create_vector_store_file(vector_store_id: str,
                                   file_id: str,
                                   user: str = Depends(get_current_user)):
    try:
        return VectorStoreFileDeleted(
            id=file_id,
            deleted=True,
            object="vector_store.file.deleted"
        )

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(e)}",
        )
