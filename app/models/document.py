from pydantic import BaseModel, Field

class DocumentSubmit(BaseModel):
    user_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)