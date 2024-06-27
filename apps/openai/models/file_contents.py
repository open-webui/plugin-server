import logging
import time
from typing import List, Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, String, LargeBinary

from apps.openai.internal.db import Base, Session

log = logging.getLogger(__name__)


####################
# Files DB Schema
####################


class FileContent(Base):
    __tablename__ = "file_content"

    id = Column(String, primary_key=True)
    content = Column(LargeBinary)


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


class FilesContentTable:

    def insert_new_file(self, id: str, content: bytes) -> Optional[FileContentModel]:
        file = FileContentModel(
            **{
                "id": id,
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
            print(f"Error creating tool: {e}")
            return None


FileContents = FilesContentTable()
