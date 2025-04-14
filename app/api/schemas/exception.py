from pydantic import BaseModel


class ExceptionResponse(BaseModel):

    exc_detail: str
    exc_message: str
