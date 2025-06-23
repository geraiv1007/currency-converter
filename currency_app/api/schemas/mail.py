from pydantic import BaseModel, EmailStr
from typing import Literal


class CurrencyInfoMail(BaseModel):

    email: EmailStr
    message: str
    info_type: Literal['live','hist','change','daily']