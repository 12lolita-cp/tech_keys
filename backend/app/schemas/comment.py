from pydantic import BaseModel


class CreateComment(BaseModel):
    message: str