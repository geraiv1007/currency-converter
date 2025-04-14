from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.db.database import Base


class User(Base):

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    username: Mapped[Optional[str]] = mapped_column(Text, unique=True)
    email: Mapped[str] = mapped_column(Text, unique=True)
    hashed_password: Mapped[Optional[str]]

    tokens: Mapped[list['JWTToken']] = relationship(back_populates='user')


class JWTToken(Base):

    __tablename__ = 'jwt_tokens'

    token_id: Mapped[str] = mapped_column(Text, primary_key=True)
    token_type: Mapped[str]
    email: Mapped[str] = mapped_column(Text, ForeignKey('users.email', ondelete='CASCADE'))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped['User'] = relationship(back_populates='tokens', passive_deletes=True, single_parent=True)