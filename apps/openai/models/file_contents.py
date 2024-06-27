import logging
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, String, LargeBinary, ForeignKey

from apps.openai.internal.db import Base, Session

log = logging.getLogger(__name__)


####################
# Files DB Schema
####################


class FileContent(Base):
    __tablename__ = "file_content"

    id = Column(String, ForeignKey("file.id", ondelete='CASCADE'), primary_key=True)
    content = Column(LargeBinary, nullable=False)


class FileContentModel(BaseModel):
    id: str
    content: bytes

    model_config = ConfigDict(from_attributes=True)


####################
# Forms
####################


class FileContentModelResponse(BaseModel):
    id: str
    content: bytes


class FileForm(BaseModel):
    id: str
    filename: str
    meta: dict = {}


class FileContentsTable:

    def insert_file_content(self, file_id: str, content: bytes) -> Optional[FileContentModel]:
        file = FileContentModel(
            **{
                "id": file_id,
                "content": content,
            }
        )

        try:
            result = FileContent(**file.model_dump())
            Session.add(result)
            Session.commit()
            Session.refresh(result)
            if result:
                return FileContentModel.model_validate(result)
            else:
                return None
        except Exception as e:
            print(f"Error inserting file content: {e}")
            return None

    def get_file_content(self, file_id: str) -> bytes:
        try:
            file_content = Session.get(FileContent, file_id)
            return file_content.content
        except Exception as e:
            print(f"Error getting file content: {e}")
            return None


FileContents = FileContentsTable()
