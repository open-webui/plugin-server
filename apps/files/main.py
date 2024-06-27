from typing import Annotated

from fastapi import FastAPI, File, Form, UploadFile
from fastapi import (
    HTTPException,
    status,
    Depends,
)
from fastapi.middleware.cors import CORSMiddleware
from openai.types import FileObject, FileDeleted

from apps.openai.models.file_contents import FileContents
from apps.openai.models.files import Files, FileForm
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
        file_bytes: bytes = file.file.read()
        inserted_file = Files.insert_new_file(
            form_data=FileForm(bytes=len(file_bytes), filename=file.filename, )
        )
        FileContents.insert_file_content(file_id=inserted_file.id, content=file_bytes)

        return FileObject(
            id=inserted_file.id,
            object=inserted_file.object,
            bytes=inserted_file.bytes,
            created_at=inserted_file.created_at,
            filename=inserted_file.filename,
            purpose=inserted_file.purpose,
            status=inserted_file.status
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
        deleted = Files.delete_file_by_id(file_id)
        return FileDeleted(
            id=file_id,
            object="file",
            deleted=deleted
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(e)}",
        )


@app.get("/{file_id}/content")
async def get_file_content(file_id: str,
                           user: str = Depends(get_current_user)):
    try:
        return FileContents.insert_file_content()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(e)}",
        )


@app.get("/{file_id}")
async def retrieve_file(file_id: str,
                        user: str = Depends(get_current_user)):
    try:
        Files.get_file_by_id(file_id)
        return FileObject(
            id=file_id,
            object="file",
            bytes=120000,
            created_at=1677610602,
            filename="file.filename",
            purpose="assistants",
            status="uploaded"
        )

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(e)}",
        )


@app.get("/")
async def list_files(
        purpose: str | None = None,
        user: str = Depends(get_current_user)

):
    try:
        files = Files.get_files()
        return {"data": [FileObject(
            id="file-id",
            object="file",
            bytes=120000,
            created_at=1677610602,
            filename="file.filename",
            purpose="assistants",
            status="uploaded"
        )]}

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(e)}",
        )
