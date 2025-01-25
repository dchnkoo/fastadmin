import pytest
import pytest_asyncio
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, Session, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from fastadmin.tools.sessions import (
    SessionManager,
    session_manager,
    asession_manager,
)

Base: DeclarativeBase = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)


@pytest.fixture(scope="session")
def engine():
    return sa.create_engine("sqlite:///:memory:")


@pytest.fixture(scope="session")
def aengine():
    return create_async_engine("sqlite+aiosqlite:///:memory:")


@pytest.fixture(scope="session")
def tables_sync(engine: sa.engine.Engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest_asyncio.fixture(scope="session")
async def tables_async(aengine: AsyncEngine):
    async with aengine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with aengine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def tables(tables_sync, tables_async):
    pass


@pytest.fixture(scope="session")
def manager(engine, aengine, tables):
    return SessionManager(engine=engine, aengine=aengine)


def test_session_manager_init_without_engines():
    with pytest.raises(ValueError):
        SessionManager()


def test_session_context_manager(manager: SessionManager):
    with manager.session(commit=True) as session:
        user = User(name="Test User")
        session.add(user)

    with manager.session() as session:
        result = session.query(User).filter_by(name="Test User").first()
        assert result is not None
        assert result.name == "Test User"


@pytest.mark.asyncio
async def test_async_session_context_manager(manager: SessionManager):
    async with manager.asession(commit=True) as scoped_session:
        user = User(name="Async Test User")
        scoped_session.add(user)

    async with manager.asession() as asession:
        result = await asession.execute(
            sa.select(User).filter_by(name="Async Test User")
        )
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.name == "Async Test User"


def test_session_manager_decorator(manager: SessionManager):
    @session_manager(commit=True)
    def create_user(name: str, session: Session):
        user = User(name=name)
        session.add(user)

    create_user("Decorated User")

    with manager.session() as session:
        result = session.query(User).filter_by(name="Decorated User").first()
        assert result is not None
        assert result.name == "Decorated User"


@pytest.mark.asyncio
async def test_async_session_manager_decorator(manager: SessionManager):
    @asession_manager(commit=True)
    async def create_user(name: str, session: AsyncSession):
        user = User(name=name)
        session.add(user)

    await create_user("Async Decorated User")

    async with manager.asession() as asession:
        result = await asession.execute(
            sa.select(User).filter_by(name="Async Decorated User")
        )
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.name == "Async Decorated User"


def test_session_manager_decorator_in_transcation_during_error(manager: SessionManager):
    @session_manager(commit=True)
    def create_user(name: str, session: Session):
        user = User(name=name)
        session.add(user)

    with manager.session() as session:
        try:
            with session.begin():
                create_user("User 1")
                raise ValueError("Error")
        except ValueError:
            pass

    with manager.session() as session:
        result = session.query(User).filter_by(name="User 1").first()
        assert result is None


@pytest.mark.asyncio
async def test_async_session_manager_decorator_in_transcation_during_error(
    manager: SessionManager,
):
    @asession_manager(commit=True)
    async def create_user(name: str, session: AsyncSession):
        user = User(name=name)
        session.add(user)

    async with manager.asession() as session:
        try:
            async with session.begin():
                await create_user("Async User 1")
                raise ValueError("Error")
        except ValueError:
            pass

    async with manager.asession() as session:
        result = await session.execute(sa.select(User).filter_by(name="Async User 1"))
        user = result.scalar_one_or_none()
        assert user is None


def test_session_manager_decorator_without_commit(manager: SessionManager):
    @session_manager()
    def create_user(name: str, session: Session):
        user = User(name=name)
        session.add(user)

    create_user("User 2")

    with manager.session() as session:
        result = session.query(User).filter_by(name="User 2").first()
        assert result is None


@pytest.mark.asyncio
async def test_async_session_manager_decorator_without_commit(manager: SessionManager):
    @asession_manager()
    async def create_user(name: str, session: AsyncSession):
        user = User(name=name)
        session.add(user)

    await create_user("Async User 2")

    async with manager.asession() as session:
        result = await session.execute(sa.select(User).filter_by(name="Async User 2"))
        user = result.scalar_one_or_none()
        assert user is None


def test_session_manager_decorator_session_is_same_during_transaction(
    manager: SessionManager,
):
    sessions = []

    @session_manager(commit=True)
    def create_user(name: str, session: Session):
        user = User(name=name)
        session.add(user)
        sessions.append(str(session))

    with manager.session() as session:
        with session.begin():
            create_user("User 3")
            create_user("User 4")

    assert sessions[0] == sessions[1]


@pytest.mark.asyncio
async def test_async_session_manager_decorator_session_is_same_during_transaction(
    manager: SessionManager,
):
    sessions = []

    @asession_manager(commit=True)
    async def create_user(name: str, session: AsyncSession):
        user = User(name=name)
        session.add(user)
        sessions.append(str(session))

    async with manager.asession() as session:
        async with session.begin():
            await create_user("Async User 3")
            await create_user("Async User 4")

    assert sessions[0] == sessions[1]


def test_session_manager_decorator_another_session(manager: SessionManager):
    sessions = []

    @session_manager(commit=True)
    def create_user(name: str, session: Session):
        user = User(name=name)
        session.add(user)
        sessions.append(str(session))

    with manager.session() as session:
        with session.begin():
            create_user("User 5")

        create_user("User 6")

    with manager.session() as session:
        with session.begin():
            create_user("User 6")

    assert sessions[0] == sessions[1]
    assert sessions[0] != sessions[2]
    assert sessions[1] != sessions[2]


@pytest.mark.asyncio
async def test_async_session_manager_decorator_another_session(manager: SessionManager):
    sessions = []

    @asession_manager(commit=True)
    async def create_user(name: str, session: AsyncSession):
        user = User(name=name)
        session.add(user)
        sessions.append(str(session))

    async with manager.asession() as session:
        async with session.begin():
            await create_user("Async User 5")

        await create_user("Async User 6")

    async with manager.asession() as session:
        async with session.begin():
            await create_user("Async User 6")

    assert sessions[0] == sessions[1]
    assert sessions[0] != sessions[2]
    assert sessions[1] != sessions[2]
