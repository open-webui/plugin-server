from uuid import uuid4

from pydantic import BaseModel, ConfigDict
from typing import List, Union, Optional, Literal
import time
import logging

from sqlalchemy import Column, String, BigInteger, Text

from apps.openai.internal.db import JSONField, Base, Session

import json

log = logging.getLogger(__name__)


####################
# Files DB Schema
####################


class File(Base):
    __tablename__ = "file"

    id = Column(String, primary_key=True)
    object = Column(String, nullable=False)
    bytes = Column(BigInteger, nullable=False)
    created_at = Column(BigInteger, nullable=False)
    filename = Column(Text, nullable=False)
    purpose = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    meta = Column(JSONField, nullable=True)


class FileModel(BaseModel):
    id: str
    object: str
    bytes: int
    created_at: int
    filename: str
    purpose: str
    status: Literal["uploaded", "processed", "error"]
    meta: str | None

    model_config = ConfigDict(from_attributes=True)


####################
# Forms
####################

class FileForm(BaseModel):
    id: str = str(uuid4())
    bytes: int
    filename: str
    meta: str | None = None  # optional field for open webui
    purpose: Literal[
        "assistants", "assistants_output", "batch", "batch_output", "fine-tune", "fine-tune-results", "vision"
    ] = "assistants"
    status: Literal["uploaded", "processed", "error"] = "uploaded"
    object: Literal["file"] = "file"
    created_at: int = int(time.time())


class FilesTable:

    def insert_new_file(self, form_data: FileForm) -> Optional[FileModel]:
        file = FileModel(
            **{
                **form_data.model_dump(),
            }
        )

        try:
            result = File(**file.model_dump())
            Session.add(result)
            Session.commit()
            Session.refresh(result)
            if result:
                return FileModel.model_validate(result)
            else:
                return None
        except Exception as e:
            print(f"Error creating tool: {e}")
            return None

    def get_file_by_id(self, id: str) -> Optional[FileModel]:
        try:
            file = Session.get(File, id)
            return FileModel.model_validate(file)
        except:
            return None

    def get_files(self) -> List[FileModel]:
        return [FileModel.model_validate(file) for file in Session.query(File).all()]

    def delete_file_by_id(self, id: str) -> bool:
        try:
            Session.query(File).filter_by(id=id).delete()
            return True
        except:
            return False

    def delete_all_files(self) -> bool:
        try:
            Session.query(File).delete()
            return True
        except:
            return False


Files = FilesTable()
