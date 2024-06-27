import logging
import time
from typing import List, Optional, Literal
from uuid import uuid4

from openai.types import FileObject
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, String, BigInteger, Text
from sqlalchemy.orm import relationship

from apps.openai.internal.db import JSONField, Base, Session
from apps.openai.models.file_contents import FileContent

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

    file_content = relationship(FileContent, backref="file", passive_deletes=True)


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
    id: str
    bytes: int
    filename: str
    meta: str | None = None  # optional field for open webui
    purpose: Literal[
        "assistants", "assistants_output", "batch", "batch_output", "fine-tune", "fine-tune-results", "vision"
    ]
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
            print(f"Error inserting new file: {e}")
            return None

    def get_file_by_id(self, file_id: str) -> Optional[FileModel]:
        try:
            file = Session.get(File, file_id)
            return FileModel.model_validate(file)
        except:
            return None

    def get_files(self, purpose: str | None) -> List[FileModel]:
        if purpose:
            return [FileModel.model_validate(file) for file in Session.query(File).filter_by(purpose=purpose)]
        else:
            return [FileModel.model_validate(file) for file in Session.query(File).all()]

    def delete_file_by_id(self, file_id: str) -> bool:
        try:
            Session.query(File).filter_by(id=file_id).delete()
            Session.commit()
            return True
        except:
            return False

    def delete_all_files(self) -> bool:
        try:
            Session.query(File).delete()
            Session.commit()
            return True
        except:
            return False

    def to_file_object(self, file: FileModel) -> FileObject:
        return FileObject(
            id=file.id,
            object=file.object,
            bytes=file.bytes,
            created_at=file.created_at,
            filename=file.filename,
            purpose=file.purpose,
            status=file.status
        )


Files = FilesTable()
