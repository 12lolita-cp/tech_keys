from pydantic import BaseModel


class CreateRequest(BaseModel):
    title: str
    description: str
    category: str
    priority: str