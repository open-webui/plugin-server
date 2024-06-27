import logging
from typing import List, Optional

from openai.types.beta import VectorStore as VectorStoreObject
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
    created_at = Column(BigInteger, nullable=False)
    file_counts = Column(BigInteger, nullable=False)
    last_active_at = Column(BigInteger, nullable=False)
    meta = Column("metadata", JSONField, nullable=True)
    name = Column(Text, nullable=True)
    object = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    usage_bytes = Column(BigInteger, nullable=False)


class VectorStoreModel(VectorStoreObject):
    model_config = ConfigDict(from_attributes=True)


####################
# Forms
####################


class VectorStoreForm(BaseModel):
    id: str
    filename: str
    meta: dict = {}


class VectorStoresTable:

    def insert_new_vector_store(self, form_data: VectorStoreModel) -> Optional[VectorStoreModel]:
        try:
            result = VectorStore(**form_data.model_dump())
            Session.add(result)
            Session.commit()
            Session.refresh(result)
            if result:
                return VectorStoreModel.model_validate(result)
            else:
                return None
        except Exception as e:
            print(f"Error inserting vector store: {e}")
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
