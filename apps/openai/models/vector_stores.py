import logging
from typing import List

from openai.types.beta import VectorStore as VectorStoreObject
from openai.types.beta.vector_store import FileCounts, ExpiresAfter
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, String, BigInteger, Text

from apps.openai.internal.db import JSONField, Base, Session

log = logging.getLogger(__name__)


####################
# Files DB Schema
####################
class FileCountsModel(FileCounts):
    model_config = ConfigDict(from_attributes=True)


class ExpiresAfterModel(ExpiresAfter):
    model_config = ConfigDict(from_attributes=True)


class VectorStoreModel(VectorStoreObject):
    model_config = ConfigDict(from_attributes=True)


class VectorStore(Base):
    __tablename__ = "vector_store"

    id = Column(String, primary_key=True)
    created_at = Column(BigInteger, nullable=False)
    last_active_at = Column(BigInteger, nullable=False)
    meta = Column(JSONField, nullable=True)
    name = Column(Text, nullable=True)
    object = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    usage_bytes = Column(BigInteger, nullable=False)
    expires_after_anchor = Column(Text, nullable=True)
    expires_after_days = Column(BigInteger, nullable=True)
    expires_at = Column(BigInteger, nullable=True)
    file_counts_in_progress = Column(BigInteger, nullable=False)
    file_counts_completed = Column(BigInteger, nullable=False)
    file_counts_failed = Column(BigInteger, nullable=False)
    file_counts_cancelled = Column(BigInteger, nullable=False)
    file_counts_total = Column(BigInteger, nullable=False)

    def to_model(self) -> VectorStoreModel:
        expires_after = None
        if self.expires_after_days:
            expires_after = ExpiresAfterModel(anchor=self.expires_after_anchor, days=self.expires_after_days)
        return VectorStoreModel(
            id=self.id,
            created_at=self.created_at,
            file_counts=FileCountsModel(cancelled=self.file_counts_cancelled,
                                        completed=self.file_counts_completed,
                                        failed=self.file_counts_failed,
                                        in_progress=self.file_counts_in_progress,
                                        total=self.file_counts_total
                                        ),
            last_active_at=self.last_active_at,
            metadata=self.meta,
            name=self.name,
            object=self.object,
            status=self.status,
            usage_bytes=self.usage_bytes,
            expires_after=expires_after,
            expires_at=self.expires_at
        )


####################
# Forms
####################


class VectorStoreForm(BaseModel):
    id: str
    filename: str
    meta: dict = {}


class VectorStoresTable:

    def insert_new_vector_store(self, form_data: VectorStoreModel) -> VectorStoreModel | None:
        try:
            anchor = None
            days = None
            if form_data.expires_after:
                anchor = form_data.expires_after.anchor
                days = form_data.expires_after.days
            result = VectorStore(**form_data.model_dump(exclude={"file_counts", "expires_after", "metadata"}),
                                 meta=form_data.metadata,
                                 expires_after_days=days,
                                 expires_after_anchor=anchor,
                                 file_counts_in_progress=form_data.file_counts.in_progress,
                                 file_counts_completed=form_data.file_counts.completed,
                                 file_counts_failed=form_data.file_counts.failed,
                                 file_counts_cancelled=form_data.file_counts.cancelled,
                                 file_counts_total=form_data.file_counts.total,
                                 )
            Session.add(result)
            Session.commit()
            Session.refresh(result)
            if result:
                return result.to_model()
            else:
                return None
        except Exception as e:
            print(f"Error inserting vector store: {e}")
            return None

    def get_vector_store_by_id(self, vector_store_id: str):
        try:
            vector_store = Session.get(VectorStore, vector_store_id)
            return VectorStoreModel.model_validate(vector_store.to_model().model_dump())
        except Exception as e:
            print(f"Error getting vector store: {e}")
            return None

    def get_vector_stores(self, limit, order, after, before) -> List[VectorStoreModel]:
        # Todo implement order, after, before
        vector_stores = Session.query(VectorStore).limit(limit).all()
        return [VectorStoreModel.model_validate(vector_store.to_model().model_dump())
                for vector_store in vector_stores]

    def delete_vector_store_by_id(self, vector_store_id: str):
        Session.query(VectorStore).filter_by(id=vector_store_id).delete()

    def delete_all_vector_stores(self) -> bool:
        try:
            Session.query(VectorStore).delete()
            return True
        except:
            return False


VectorStores = VectorStoresTable()
