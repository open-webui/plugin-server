from typing import Annotated

from fastapi import FastAPI, File, Form, UploadFile
from fastapi import (
    HTTPException,
    status,
    Depends,
)
from fastapi.middleware.cors import CORSMiddleware
from openai.types import FileObject, FileDeleted
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


@app.post("/")
async def upload_file(purpose: Annotated[str, Form()],
                      file: Annotated[UploadFile, File()],
                      user: str = Depends(get_current_user)):
    try:
        return FileObject(
            id="file-abc123",
            object="file",
            bytes=120000,
            created_at=1677610602,
            filename="file.filename",
            purpose=purpose,
            status="uploaded"
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(e)}",
        )


@app.delete("/{file_id}")
async def delete_file(file_id: str,
                      user: str = Depends(get_current_user)):
    try:
        return FileDeleted(
            id=file_id,
            object="file",
            deleted=True
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(e)}",
        )
