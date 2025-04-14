from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):

    metadata = MetaData(schema='currency_converter')

    @property
    def attrs(self):
        cols = {col.key: getattr(self, col.key) for col in list(self.__table__.c)}
        return cols
