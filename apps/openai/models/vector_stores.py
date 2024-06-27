from pydantic import BaseModel, ConfigDict
from typing import List, Union, Optional
import time
import logging

from sqlalchemy import Column, String, BigInteger, Text

from apps.openai.internal.db import JSONField, Base, Session

import json

log = logging.getLogger(__name__)

####################
# Files DB Schema
####################


class VectorStore(Base):
    __tablename__ = "file"

    id = Column(String, primary_key=True)
    user_id = Column(String)
    filename = Column(Text)
    meta = Column(JSONField)
    created_at = Column(BigInteger)


class VectorStoreModel(BaseModel):
    id: str
    user_id: str
    filename: str
    meta: dict
    created_at: int  # timestamp in epoch

    model_config = ConfigDict(from_attributes=True)


####################
# Forms
####################


class FileModelResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    meta: dict
    created_at: int  # timestamp in epoch


class FileForm(BaseModel):
    id: str
    filename: str
    meta: dict = {}


class FilesTable:

    def insert_new_file(self, user_id: str, form_data: FileForm) -> Optional[FileModel]:
        file = FileModel(
            **{
                **form_data.model_dump(),
                "user_id": user_id,
                "created_at": int(time.time()),
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
