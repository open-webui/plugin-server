import logging
import time
from typing import List, Optional, Literal

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
    status_details = Column(Text, nullable=True)
    meta = Column(JSONField, nullable=True)

    file_content = relationship(FileContent, backref="file", passive_deletes=True)


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


class FileModel(FileObject):
    model_config = ConfigDict(from_attributes=True)


class FilesTable:

    def insert_new_file(self, form_data: FileModel) -> Optional[FileModel]:
        try:
            result = File(**form_data.model_dump())
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

    def get_file_by_id(self, file_id: str) -> FileModel:
        file = Session.get(File, file_id)
        return FileModel.model_validate(file)

    def get_files(self, purpose: str | None) -> List[FileModel]:
        if purpose:
            return [FileModel.model_validate(file)
                    for file in Session.query(File).filter_by(purpose=purpose)]
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


Files = FilesTable()
