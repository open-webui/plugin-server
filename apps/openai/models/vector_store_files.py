import logging
from typing import Optional

from openai.types.beta.vector_stores.vector_store_file import VectorStoreFile as VectorStoreFileObject, LastError, \
    ChunkingStrategy, ChunkingStrategyStatic, ChunkingStrategyOther, ChunkingStrategyStaticStatic
from pydantic import ConfigDict
from sqlalchemy import Column, String, BigInteger, Text

from apps.openai.internal.db import JSONField, Base, Session

log = logging.getLogger(__name__)


####################
# Files DB Schema
####################


class VectorStoreFile(Base):
    __tablename__ = "vector_store_file"

    filename = Column(Text)
    meta = Column(JSONField)

    id = Column(String, primary_key=True)
    created_at = Column(BigInteger, nullable=False)
    last_error_code = Column(Text, nullable=True)
    last_error_message = Column(Text, nullable=True)
    object = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    usage_bytes = Column(BigInteger, nullable=False)
    vector_store_id = Column(Text, nullable=False)
    chunking_strategy_static_chunk_overlap_tokens = Column(BigInteger, nullable=True)
    chunking_strategy_static_max_chunk_size_tokens = Column(BigInteger, nullable=True)
    chunking_strategy_type = Column(Text, nullable=True)

    def get_chunking_strategy(self) -> ChunkingStrategy | None:
        if self.chunking_strategy_type == "static":
            return ChunkingStrategyStatic(
                type="static",
                static=ChunkingStrategyStaticStatic(
                    chunk_overlap_tokens=self.chunking_strategy_static_chunk_overlap_tokens,
                    max_chunk_size_tokens=self.chunking_strategy_static_max_chunk_size_tokens,
                )
            )
        else:
            return ChunkingStrategyOther(type="other")

    def get_last_error(self) -> LastError | None:
        if self.last_error_code is not None:
            return LastError(
                code=self.last_error_code,
                message=self.last_error_message
            )

    def to_model(self):
        return VectorStoreFileModel(
            id=self.id,
            created_at=self.created_at,
            last_error_code=self.get_last_error(),
            object=self.object,
            status=self.status,
            usage_bytes=self.usage_bytes,
            vector_store_id=self.vector_store_id,
            chunking_strategy=self.get_chunking_strategy(),
        )

    # class ChunkingStrategyModel(ChunkingStrategy):


#     code: Literal["internal_error", "file_not_found", "parsing_error", "unhandled_mime_type"]
#     message: str
# 
# 
# class LastErrorModel(LastError):
#     code: Literal["internal_error", "file_not_found", "parsing_error", "unhandled_mime_type"]
#     message: str


class VectorStoreFileModel(VectorStoreFileObject):
    model_config = ConfigDict(from_attributes=True)


class VectorStoreFilesTable:

    def insert_new_vector_store_file(self,
                                     vector_store_id: str,
                                     model: VectorStoreFileModel) -> VectorStoreFileModel | None:

        try:
            chunking_strategy_static_chunk_overlap_tokens = None
            chunking_strategy_static_max_chunk_size_tokens = None
            chunking_strategy_type = None
            if model.chunking_strategy is not None and model.chunking_strategy.type == "static":
                chunking_strategy_type = "static"
                chunking_strategy_static_max_chunk_size_tokens = model.chunking_strategy.static.max_chunk_size_tokens
                chunking_strategy_static_chunk_overlap_tokens = model.chunking_strategy.static.chunk_overlap_tokens
            else:
                chunking_strategy_type = "other"

            result = VectorStoreFile(**model.model_dump(exclude={"chunking_strategy", "last_error"}),
                                     last_error_code=None,
                                     last_error_message=None,
                                     chunking_strategy_static_chunk_overlap_tokens=chunking_strategy_static_chunk_overlap_tokens,
                                     chunking_strategy_static_max_chunk_size_tokens=chunking_strategy_static_max_chunk_size_tokens,
                                     chunking_strategy_type=chunking_strategy_type,
                                     )
            Session.add(result)
            Session.commit()
            Session.refresh(result)
            if result:
                return VectorStoreFileModel.model_validate(result.to_model().model_dump())
            else:
                return None

        except Exception as e:
            print(f"Error creating tool: {e}")
            return None

    def get_vector_store_file_by_id(self, vector_store_id: str, file_id: str) -> Optional[VectorStoreFileModel]:
        try:
            vector_store_file = Session.query(VectorStoreFile).filter_by(id=file_id, vector_store_id=vector_store_id).first()
            return VectorStoreFileModel.model_validate(vector_store_file.to_model().model_dump())
        except:
            return None

    def delete_vector_store_file_by_id(self, file_id: str) -> bool:
        try:
            Session.query(VectorStoreFile).filter_by(id=file_id).delete()
            return True
        except:
            return False


VectorStoreFiles = VectorStoreFilesTable()
