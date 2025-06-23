from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from currency_app.broker.kafka_broker import broker
from currency_app.api.endpoints.auth import auth_router
from currency_app.api.endpoints.currency import currency_router
from currency_app.api.endpoints.user import user_router
from currency_app.exceptions.exceptions import UserAlreadyExistsException
from currency_app.exceptions.handlers import register_exception_handlers, base_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.connect()
    yield
    await broker.close()

app = FastAPI(
    title='Currency converter',
    description='Currency converter with live and historical exchange rates',
    version='0.1.0',
    default_response_class=ORJSONResponse,
    docs_url="/docs",
    lifespan=lifespan
)
register_exception_handlers(app)
app.add_exception_handler(UserAlreadyExistsException, base_exception_handler)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(currency_router)