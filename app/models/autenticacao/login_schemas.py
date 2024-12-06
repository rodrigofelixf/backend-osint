from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class ErrorResponse(BaseModel):
    detail: str