from pydantic import BaseModel


class MessageResponse(BaseModel):
    detail: str


class DeleteResponse(BaseModel):
    message: str


class ImportResponse(BaseModel):
    imported: int
    skipped: int
    errors: list[str]
