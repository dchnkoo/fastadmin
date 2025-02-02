import pytest
import pytest_asyncio

from .tables import FastBase, User, Post, Comment

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker, Session
import sqlalchemy as _sa


@pytest.fixture(scope="session")
def create_engine():
    return _sa.create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )


@pytest.fixture(scope="function")
def engine(create_engine: _sa.Engine):
    with create_engine.connect() as conn:
        conn.execute(_sa.text("PRAGMA foreign_keys=ON"))
    FastBase.metadata.create_all(create_engine)
    yield create_engine
    FastBase.metadata.drop_all(create_engine)
    create_engine.dispose()


@pytest.fixture(scope="session")
def create_async_engine_fixture():
    return create_async_engine(
        "sqlite+aiosqlite:///:memory:", connect_args={"check_same_thread": False}
    )


@pytest_asyncio.fixture(scope="function")
async def aengine(create_async_engine_fixture: AsyncEngine):
    async with create_async_engine_fixture.connect() as conn:
        await conn.execute(_sa.text("PRAGMA foreign_keys=ON"))
        await conn.run_sync(FastBase.metadata.create_all)
    yield create_async_engine_fixture
    async with create_async_engine_fixture.begin() as conn:
        await conn.run_sync(FastBase.metadata.drop_all)
    await create_async_engine_fixture.dispose()


@pytest.fixture(scope="function")
def session(engine: _sa.Engine):
    Session = sessionmaker(bind=engine)
    return Session()


@pytest.fixture(scope="function")
def user(session: Session):
    user = User(id=1, name="John Doe", age=30)
    session.add(user)
    session.commit()
    return user


@pytest.fixture(scope="function")
def post(user: User, session: Session):
    post = Post(
        id=1, title="First Post", content="This is the first post", user_id=user.id
    )
    session.add(post)
    session.commit()
    return post


@pytest.fixture(scope="function")
def comment(post: Post, user: User, session: Session):
    comment = Comment.insert().values(
        id=1, content="Nice post!", post_id=post.id, user_id=user.id
    )
    session.execute(comment)
    session.commit()
    return comment
