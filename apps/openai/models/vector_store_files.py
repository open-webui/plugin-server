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


class VectorStoreFile(Base):
    __tablename__ = "vector_store_file"

    id = Column(String, primary_key=True)
    user_id = Column(String)
    filename = Column(Text)
    meta = Column(JSONField)
    created_at = Column(BigInteger)


class VectorStoreFileModel(BaseModel):
    id: str
    user_id: str
    filename: str
    meta: dict
    created_at: int  # timestamp in epoch

    model_config = ConfigDict(from_attributes=True)


####################
# Forms
####################


class VectorStoreFileModelResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    meta: dict
    created_at: int  # timestamp in epoch


class VectorStoreFileForm(BaseModel):
    id: str
    filename: str
    meta: dict = {}


class VectorStoreFilesTable:

    def insert_new_vector_store_file(self, user_id: str, form_data: VectorStoreFileForm) -> Optional[VectorStoreFileModel]:
        file = VectorStoreFileModel(
            **{
                **form_data.model_dump(),
                "user_id": user_id,
                "created_at": int(time.time()),
            }
        )

        try:
            result = VectorStoreFile(**file.model_dump())
            Session.add(result)
            Session.commit()
            Session.refresh(result)
            if result:
                return VectorStoreFileModel.model_validate(result)
            else:
                return None
        except Exception as e:
            print(f"Error creating tool: {e}")
            return None

    def get_vector_store_file_by_id(self, id: str) -> Optional[VectorStoreFileModel]:
        try:
            vector_store_file = Session.get(VectorStoreFile, id)
            return VectorStoreFileModel.model_validate(vector_store_file)
        except:
            return None

    def get_vector_store_files(self) -> List[VectorStoreFileModel]:
        return [VectorStoreFileModel.model_validate(vector_store_file) for vector_store_file in Session.query(VectorStoreFile).all()]

    def delete_vector_store_file_by_id(self, id: str) -> bool:
        try:
            Session.query(VectorStoreFile).filter_by(id=id).delete()
            return True
        except:
            return False

    def delete_all_vector_store_files(self) -> bool:
        try:
            Session.query(VectorStoreFile).delete()
            return True
        except:
            return False


VectorStoreFiles = VectorStoreFilesTable()
