from fastadmin.conf import FastAdminConfig as _config, SECONDS as _SECONDS

from starlette.middleware.base import BaseHTTPMiddleware as _StarletteHTTP
from starlette.requests import cookie_parser

from abc import ABC, abstractmethod

import fastapi as _fa
import pydantic as p
import typing as _t
import datetime as _date
import jwt as _jwt

if _t.TYPE_CHECKING:
    from fastadmin.utils.database.tables import AdminUser


CookieSettings: _t.TypeAlias = dict[
    _t.Literal[
        "max_age", "expires", "path", "domain", "secure", "httponly", "samesite"
    ],
    _t.Any,
]
DateTimeStr: _t.TypeAlias = str

Cookies: _t.TypeAlias = dict[str, str]
ActionsKwargs: _t.TypeAlias = dict[str, _t.Any]


class Token(p.BaseModel):
    life: _SECONDS
    name: str
    algorithm: _t.Literal["HS256", "HS384", "HS512"]


class AbsractJWTMiddleware(ABC, _StarletteHTTP):
    secret = _config.secret_token

    access = Token(
        life=_config.access_token_life,
        name=_config.access_token_name,
        algorithm="HS256",
    )

    refresh = Token(
        life=_config.refresh_token_life,
        name=_config.refresh_token_name,
        algorithm="HS512",
    )

    @classmethod
    async def get_secret(cls) -> str:
        if callable(cls.secret):
            return await cls.secret()

        return cls.secret

    @classmethod
    async def get_token(cls, algorithm: _t.LiteralString, **playload) -> str:
        secret = await cls.get_secret()

        token = _jwt.encode(playload, secret, algorithm)

        return token

    @classmethod
    @abstractmethod
    def get_access_playload(cls, user: type[object]) -> dict:
        ...

    @classmethod
    @abstractmethod
    def get_refresh_playload(cls, user: type[object]) -> dict:
        ...

    @classmethod
    async def check_token(
        cls, token: str, algorithm: _t.LiteralString
    ) -> dict[str, _t.Any]:
        secret = await cls.get_secret()

        try:
            data = _jwt.decode(token, secret, algorithms=[algorithm])

        except _jwt.ExpiredSignatureError:
            raise _fa.HTTPException(
                status_code=_fa.status.HTTP_401_UNAUTHORIZED,
                detail="JWT token expired. Please get new token!",
            )

        except _jwt.InvalidTokenError:
            raise _fa.HTTPException(
                status_code=_fa.status.HTTP_400_BAD_REQUEST,
                detail="Invalid JWT token. Check your token!",
            )

        except Exception:
            raise _fa.HTTPException(
                status_code=_fa.status.HTTP_403_FORBIDDEN, detail="JWT token missing."
            )

        return data

    @classmethod
    def get_expires_str(cls, value: _date.datetime) -> DateTimeStr:
        return value.strftime("%a, %d-%b-%Y %T GMT")

    @staticmethod
    def get_expires_date(value: _SECONDS) -> _date.datetime:
        return _date.datetime.now(_date.timezone.utc) + _date.timedelta(seconds=value)

    @classmethod
    def access_playload(cls, **playload) -> dict:
        return playload | {"exp": cls.get_expires_date(cls.access.life)}

    @classmethod
    def refresh_playload(cls, **playload) -> dict:
        return playload | {"exp": cls.get_expires_date(cls.refresh.life)}

    @classmethod
    def set_cookie_to_response(
        cls,
        resposne: _fa.Response,
        cookie_name: str,
        cookie_value: str,
        **kw: CookieSettings,
    ) -> None:
        resposne.set_cookie(key=cookie_name, value=cookie_value, **kw)

    @classmethod
    async def set_access_token_to_response(
        cls, response: _fa.Response, playload: dict, **kw: CookieSettings
    ) -> None:
        credentials = cls.access_playload(**playload)

        access_token: str = await cls.get_token(cls.access.algorithm, **credentials)

        cls.set_cookie_to_response(
            resposne=response,
            cookie_name=cls.access.name,
            cookie_value=access_token,
            expires=cls.get_expires_str(credentials.get("exp")),
            **kw,
        )

    @classmethod
    async def set_refresh_token_to_response(
        cls, response: _fa.Response, playload: dict, **kw: CookieSettings
    ) -> None:
        credentials = cls.refresh_playload(**playload)

        refresh_token: str = await cls.get_token(cls.refresh.algorithm, **credentials)

        cls.set_cookie_to_response(
            resposne=response,
            cookie_name=cls.refresh.name,
            cookie_value=refresh_token,
            expires=cls.get_expires_str(credentials.get("exp")),
            **kw,
        )

    @classmethod
    async def set_cookies_to_reponse(
        cls, response: _fa.Response, playload: dict, **kw: CookieSettings
    ):
        await cls.set_refresh_token_to_response(
            response=response, playload=playload, **kw
        )

        await cls.set_access_token_to_response(
            response=response, playload=playload, **kw
        )

    @classmethod
    async def get_access_credentials(cls, request: _fa.Request) -> dict:
        cookies: dict[str, str] = request.cookies

        token = cookies.get(cls.access.name)

        return await cls.check_token(token, cls.access.algorithm)

    @classmethod
    async def get_access_credentials_or_none(
        cls, request: _fa.Request
    ) -> _t.Optional[dict]:
        try:
            return await cls.get_access_credentials(request=request)
        except _fa.HTTPException:
            return None

    @classmethod
    async def get_refresh_credentials(cls, request: _fa.Request) -> dict:
        cookies: dict[str, str] = request.cookies

        token = cookies.get(cls.refresh.name)

        return await cls.check_token(token, cls.refresh.algorithm)

    @classmethod
    async def get_refresh_credentials_or_none(
        cls, request: _fa.Request
    ) -> _t.Optional[dict]:
        try:
            return await cls.get_refresh_credentials(request=request)
        except _fa.HTTPException:
            return None

    @staticmethod
    async def change_cookies_in_request(
        request: _fa.Request,
        action: _t.Awaitable[_t.Callable[[Cookies, ActionsKwargs], None]],
        **kw: ActionsKwargs,
    ) -> None:
        headers = request.headers

        headers_copy = headers.mutablecopy()

        cookies = headers_copy.get("cookie", "")

        parse_cookie = cookie_parser(cookie_string=cookies)

        await action(parse_cookie, **kw)

        updated_cookies = "; ".join([f"{k}={v}" for k, v in parse_cookie.items()])

        headers_copy["cookie"] = updated_cookies

        request.scope["headers"] = headers_copy.raw
        delattr(request, "_headers")

    @staticmethod
    async def change_cookie(cookie: Cookies, name: str, value: str) -> None:
        """
        Use this method in :method:`change_cookies_in_request` function.
        """
        cookie[name] = value

    @staticmethod
    async def delete_cookie(cookie: Cookies, name: str) -> None:
        """
        Use this method in :method:`change_cookies_in_request` function.
        """
        del cookie[name]

    @abstractmethod
    async def dispatch(
        self,
        request: _fa.Request,
        call_next: _t.Callable[[_fa.Request], _t.Awaitable[_fa.Response]],
    ) -> _fa.Response:
        ...


user_id: _t.TypeAlias = int


class FastAdminJWT(AbsractJWTMiddleware):
    @classmethod
    def get_access_playload(cls, user: type["AdminUser"]) -> dict:
        return dict(email=user.email)

    @classmethod
    def get_refresh_playload(cls, user: type["AdminUser"]) -> dict:
        return dict(id=user.id)

    @classmethod
    async def get_access_credentials(cls, request: _fa.Request) -> p.EmailStr:
        data = await super().get_access_credentials(request)

        return data.get("email")

    @classmethod
    async def get_refresh_credentials(cls, request: _fa.Request) -> user_id:
        data = await super().get_refresh_credentials(request)

        return data.get("id")

    @classmethod
    async def set_access_token_to_response(
        cls, response: _fa.Response, user: type["AdminUser"], **kw: CookieSettings
    ) -> None:
        playload = cls.get_access_playload(user=user)

        await super().set_access_token_to_response(response, playload, **kw)

    @classmethod
    async def set_refresh_token_to_response(
        cls, response: _fa.Response, user: type["AdminUser"], **kw: CookieSettings
    ) -> None:
        playload = cls.get_refresh_playload(user=user)

        await super().set_refresh_token_to_response(response, playload, **kw)

    @classmethod
    async def set_cookies_to_reponse(
        cls, response: _fa.Response, user: type["AdminUser"], **kw: CookieSettings
    ):
        await cls.set_access_token_to_response(response, user, **kw)
        await cls.set_refresh_token_to_response(response, user, **kw)

    async def dispatch(
        self,
        request: _fa.Request,
        call_next: _t.Callable[[_fa.Request], _t.Awaitable[_fa.Response]],
    ) -> _fa.Response:
        try:
            await self.get_access_credentials(request=request)

        except _fa.HTTPException:
            user_id = await self.get_refresh_credentials_or_none(request=request)

            if user_id is None:
                raise _fa.HTTPException(status_code=_fa.status.HTTP_401_UNAUTHORIZED)

            from fastadmin.metadata import FastAdminMeta

            admin = FastAdminMeta._get_admin()

            session = admin.get_session()

            async with session() as session:
                data = await admin.get(
                    session=session,
                    table=(admin.email,),
                    where=admin.id == user_id,
                    all_=False,
                )

            email = data.data

            playload = self.access_playload(email=email)

            token = await self.get_token(self.access.algorithm, **playload)

            await self.change_cookies_in_request(
                request=request,
                action=self.change_cookie,
                name=self.access.name,
                value=token,
            )

            return await call_next(request)

        except Exception as exc:
            print(exc)
            raise _fa.HTTPException(status_code=_fa.status.HTTP_400_BAD_REQUEST)

        return await call_next(request)
