from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProjectFileBase(BaseModel):
    project_id: str
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

class ProjectFileCreate(ProjectFileBase):
    pass

class ProjectFileRead(ProjectFileBase):
    id: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

class ProjectFileList(BaseModel):
    files: List[ProjectFileRead]
    total: int
