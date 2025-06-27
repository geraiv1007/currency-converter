from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from currency_app.broker.admin import KafkaAdmin
from currency_app.broker.broker import Broker
from currency_app.api.endpoints.auth import auth_router
from currency_app.api.endpoints.currency import currency_router
from currency_app.api.endpoints.health import health_router
from currency_app.api.endpoints.user import user_router
from currency_app.exceptions.exceptions import UserAlreadyExistsException
from currency_app.exceptions.handlers import register_exception_handlers, base_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    admin = KafkaAdmin()
    await admin.start()
    await admin.create_topic('currency_info', 2, 1)
    app.state.admin_client = admin
    kafka_broker = Broker()
    await kafka_broker.connect()
    kafka_broker.create_publisher('currency_info')
    app.state.kafka_broker = kafka_broker
    yield
    await kafka_broker.disconnect()
    await admin.close()


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
app.include_router(health_router)