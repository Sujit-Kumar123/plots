from pydantic import BaseModel


class ValidateSessionRequest(BaseModel):
    token_hash: str
