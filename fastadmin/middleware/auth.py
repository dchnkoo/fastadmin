from fastapi.requests import HTTPConnection
from starlette.authentication import AuthCredentials, AuthenticationBackend, BaseUser


class FastAdminAuthMiddleware(AuthenticationBackend):
    async def authenticate(
        self, conn: HTTPConnection
    ) -> tuple[AuthCredentials, BaseUser] | None:
        ...
