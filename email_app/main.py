from fastapi import FastAPI

from email_app.routers.mail import mail_router


app = FastAPI()

@mail_router.get('/ping')
async def health_check():
    return 'Kafka is alive!'

app.include_router(mail_router)