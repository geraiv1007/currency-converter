from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.api.endpoints.auth import auth_router
from app.api.endpoints.currency import currency_router
from app.api.endpoints.user import user_router
from app.exceptions.exceptions import UserAlreadyExistsException
from app.exceptions.handlers import register_exception_handlers, base_exception_handler


app = FastAPI(
    title='Currency converter',
    description='Currency converter with live and historical exchange rates',
    version='0.1.0',
    default_response_class=ORJSONResponse,
    docs_url="/docs"
)
register_exception_handlers(app)
app.add_exception_handler(UserAlreadyExistsException, base_exception_handler)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(currency_router)