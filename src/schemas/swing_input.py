from fastapi import UploadFile
from pydantic import BaseModel

class SwingInput(BaseModel):
    video: UploadFile