from fastapi.security import APIKeyHeader


api_key_refresh_token = APIKeyHeader(
    name='X-Refresh-Token',
    description='Header must be named "X-Refresh-Token"',
    auto_error=False,
    scheme_name='RefreshToken'
)
api_key_access_token = APIKeyHeader(
    name='Authorization',
    description='Header must be named "Authorization" and contain "bearer"',
    auto_error=False,
    scheme_name='AccessToken'
)