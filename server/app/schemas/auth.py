from pydantic import BaseModel


class AuthLoginRequest(BaseModel):
    code: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"