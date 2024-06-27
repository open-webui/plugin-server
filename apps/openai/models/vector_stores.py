import logging
import time
from typing import List, Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, String, BigInteger, Text

from apps.openai.internal.db import JSONField, Base, Session

log = logging.getLogger(__name__)


####################
# Files DB Schema
####################


class VectorStore(Base):
    __tablename__ = "vector_store"

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


class VectorStoreModelResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    meta: dict
    created_at: int  # timestamp in epoch


class VectorStoreForm(BaseModel):
    id: str
    filename: str
    meta: dict = {}


class VectorStoresTable:

    def insert_new_vector_store(self, user_id: str, form_data: VectorStoreForm) -> Optional[VectorStoreModel]:
        vector_store = VectorStoreModel(
            **{
                **form_data.model_dump(),
                "user_id": user_id,
                "created_at": int(time.time()),
            }
        )

        try:
            result = VectorStore(**vector_store.model_dump())
            Session.add(result)
            Session.commit()
            Session.refresh(result)
            if result:
                return VectorStoreModel.model_validate(result)
            else:
                return None
        except Exception as e:
            print(f"Error creating tool: {e}")
            return None

    def get_vector_store_by_id(self, id: str) -> Optional[VectorStoreModel]:
        try:
            vector_store = Session.get(VectorStore, id)
            return VectorStoreModel.model_validate(vector_store)
        except:
            return None

    def get_vector_stores(self) -> List[VectorStoreModel]:
        return [VectorStoreModel.model_validate(vector_store) for vector_store in Session.query(VectorStore).all()]

    def delete_vector_store_by_id(self, id: str) -> bool:
        try:
            Session.query(VectorStore).filter_by(id=id).delete()
            return True
        except:
            return False

    def delete_all_vector_stores(self) -> bool:
        try:
            Session.query(VectorStore).delete()
            return True
        except:
            return False


VectorStores = VectorStoresTable()
