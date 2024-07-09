from fastadmin.conf import FastAdminConfig
from fastadmin.utils import types

import pydantic as _p
import fastapi as _fa
import typing as _t

if _t.TYPE_CHECKING:
    from fastadmin.middleware.jwt import FastAdminJWT
    from fastadmin.utils.words import AdminWords
    from sqlalchemy.orm import DeclarativeBase


class Autheficate(_p.BaseModel):
    email: _p.EmailStr
    password: _p.SecretStr


class FastAdmin(_fa.FastAPI):
    """
    :class:`FastAdmin` is aimed at very easy creation and interaction from the admin panel
    with full customization of each component individually for each of your Sqlalchemy ORM models.

    Such easy and quick customization is possible thanks
    to the integration with the :module:`FastUI` framework, which also depends on :module:`FastAPI`.

    `FastAdmin` is a completely asynchronous framework that provides
    its own CRUD model for interacting with your database.

    Simple example:
    ```python
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
    import sqlalchemy as sa

    from fastadmin.utils.descriptor.clas import classproperty
    from fastadmin.metadata import FastAdminMeta
    from fastadmin import FastAdmin


    class Base(DeclarativeBase):
        ...


    class Worker(FastAdminMeta, Base):
        __tablename__ = "some_worker"

        repr = {
            "exclude": ["id"]
        }

        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.String, nullable=False)


    from fastadmin.utils.database.tables import AdminUser


    class User(Base, FastAdminMeta):
        __tablename__ = "some_user"

        @classproperty
        def admin(cls):
            return {
                "exclude": ["id", "name"]
            }

        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(nullable=True)
        worker: Mapped[int] = mapped_column(
            sa.ForeignKey("some_worker.id", link_to_name=True),
            nullable=False,
            doc="Worker",
            primary_key=True,
        )


    app = FastAdmin(sql_db_uri="postgresql+asyncpg://test:test@localhost:5432/test", secret_token="sdihsbkfh")

    ```

    """

    def __init__(
        self,
        *,
        sql_db_uri: types.URI_WITH_ASYNC_DRIVER,
        secret_token: _t.Union[
            _t.Callable[[], _t.Coroutine[_t.Any, _t.Any, str]], _t.LiteralString
        ],
        sqlalchemy_metadata: _t.Optional[type["DeclarativeBase"]],
        admin_panel_words: _t.Optional["AdminWords"] = None,
        admin_table_name: str = "admin_user",
        admin_middleware: _t.Optional[type["FastAdminJWT"]] = None,
        auth_model: type[_p.BaseModel] = Autheficate,
        path: str = "/administrator",
        default_title: str = "Fast Admin",
        api_root_url: str = "/api",
        api_path_mode: _t.Optional[_t.Literal["append", "query"]] = None,
        **fastapi_options,
    ) -> None:
        """
        :param sql_db_uri: `FastAdmin` uses a completely asynchronous approach \
            to interacting with the database, it needs an asynchronous driver to \
            establish an asynchronous connection to your SQL database.

        :param secret_token: the framework provides its own admin model and class \
            for JWT authentication and it requires a secret key to generate tokens. \
            You can provide either a regular string with a key or an asynchronous function \
            that will be called every time to get the key and it must return a string.

        :param admin_middleware: As mentioned above, the framework provides its own \
            integration of the administrative user with its middleware, but if you suddenly want \
            to change the administrative user and rewrite the user authentication logic for yourself, \
            you can use your own middleware that comes from `FastAdminJWT`.

        :param path: this is path to your adminstrative application. Do not under any \
            circumstances mount the `FastAdmin` as this will break all application paths \
            and it will not be able to display the UI.

        :param default_title: this title displays in navbars of this app.

        :param api_root_url: Under the hood, `FastAdmin` uses a UI builder - `FastUI`, \
            it needs a prefix before each endpoint that it will recognize in `FastAPI` endpoints. \
            The default value is /api.

        :param sqlalchemy_metadata: `FastAdmin` provides an administrative user for authentication \
            and rights management in the admin panel. But if you intend to create your admin user \
            you can leave this parameter as None, but in this case you will need to write your middleware \
            to authenticate the admin. Or inherit permission model from the `fastadmin.utils.database.tables` \
            in the administrator table.

        :param api_path_mode: This parameter determines how the application should deal with queries \
            in the url by default, it is append, that is, the application will not delete all queries \
            before adding a new one, but on the contrary will add it to the existing ones. \
            The query parameter does the opposite.

        :param fastapi_options: `FastAdmin` inherits `FastAPI`, and this is a router, \
            so you can specify the configuration for this application as for a regular `FastAPI` application.
        """
        super().__init__(**fastapi_options)

        FastAdminConfig.sql_db_uri = self.sql_db_uri = sql_db_uri
        FastAdminConfig.default_title = self.default_title = default_title
        FastAdminConfig.api_root_url = self.api_root_url = api_root_url
        FastAdminConfig.api_path_mode = self.api_path_mode = api_path_mode
        FastAdminConfig.api_path_strip = self.api_path_strip = path
        FastAdminConfig.secret_token = self.secret_token = secret_token
        FastAdminConfig.sqlalchemy_metadata = (
            self.sqlalchemy_metadata
        ) = sqlalchemy_metadata
        FastAdminConfig.admin_table_name = self.admin_table_name = admin_table_name
        FastAdminConfig.auth_model = self.auth_model = auth_model

        if sqlalchemy_metadata is not None:
            from fastadmin.utils.database.tables import AdminUser  # noqa F401

        if admin_middleware is None:
            from fastadmin.middleware.jwt import FastAdminJWT

            FastAdminConfig.admin_middleware = self.admin_middleware = FastAdminJWT

        else:
            FastAdminConfig.admin_middleware = self.admin_middleware = admin_middleware

        if admin_panel_words is not None:
            FastAdminConfig.words = self.admin_panel_words = admin_panel_words

        else:
            from fastadmin.utils.words import AdminWords

            FastAdminConfig.words = self.admin_panel_words = AdminWords()

        from fastadmin.ui.main import ui, auth

        self.mount(path=api_root_url, app=auth)
        auth.mount(path="", app=ui)

        from fastadmin.ui.main import main

        self.mount(path=path, app=main)
