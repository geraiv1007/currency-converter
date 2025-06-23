import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from currency_app.db.models import JWTToken


class JWTRepository:

    def __init__(self, async_session: AsyncSession):
        self.async_session = async_session

    async def add_user_tokens(self, tokens: tuple[str, str]):
        payloads = {
            token: jwt.decode(token, options={'verify_signature': False})
            for token in tokens
        }
        tokens = [
            JWTToken(
                token_id=token_id,
                token_type=payload['type'],
                email=payload['sub'],
            )
            for token_id, payload in payloads.items()
        ]
        self.async_session.add_all(tokens)

    async def check_token_revoked(self, token_id: str) -> bool:
        stmt = (
            select(JWTToken.email, JWTToken.revoked)
            .where(JWTToken.token_id == token_id)
        )
        email, status = (await self.async_session.execute(stmt)).one()

        if status:
            await self.revoke_user_tokens(email)

        return status

    async def revoke_user_tokens(self, email: str):
        stmt = (
            select(JWTToken)
            .where(JWTToken.email == email)
            .where(JWTToken.revoked == False)
        )
        tokens = (await self.async_session.scalars(stmt)).all()
        for token in tokens:
            token.revoked = True
