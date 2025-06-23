import inspect
import sys
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse

from currency_app.api.schemas.exception import ExceptionResponse
from currency_app.exceptions.exceptions import AuthException, UserAlreadyExistsException


def register_exception_handlers(app: FastAPI):
    from . import exceptions

    for name, obj in inspect.getmembers(sys.modules[exceptions.__name__]):
        if inspect.isclass(obj) and issubclass(obj, AuthException) and obj is not AuthException:
            app.add_exception_handler(obj, base_exception_handler)


async def base_exception_handler(request: Request, exc: AuthException):
    error = jsonable_encoder(
        ExceptionResponse(
            exc_detail=exc.detail,
            exc_message=exc.message
        )
    )
    return ORJSONResponse(
        status_code=exc.status_code,
        content=error
    )