"""Shared fixtures for the project's tests.

Every test gets:
* a brand-new SQLite database file in a temporary folder (tests never see
  each other's data, and never touch training.db)
* `get_db` and `get_settings` replaced with test versions (dependency_overrides)
* an async HTTPX client talking to the app in-process
* factories to create users and courses directly in the database, and a
  helper that makes the Authorization header for any user
"""

from collections.abc import AsyncIterator, Awaitable, Callable
from pathlib import Path

import httpx
import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings, get_settings
from app.database import Base, get_db
from app.main import app
from app.models import Course, User
from app.security import create_access_token, hash_password

PASSWORD = 'Password123'
UserFactory = Callable[..., Awaitable[User]]
CourseFactory = Callable[..., Awaitable[Course]]


@pytest.fixture
def anyio_backend() -> str:
    return 'asyncio'


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        database_url=f'sqlite+aiosqlite:///{tmp_path / "test.db"}',
        jwt_secret_key='test-secret-key-that-is-long-enough-0123456789',
        upload_dir=tmp_path / 'uploads',
        max_upload_mb=1,
    )


@pytest.fixture
async def session_factory(settings: Settings) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine(settings.database_url)

    @event.listens_for(engine.sync_engine, 'connect')
    def foreign_keys_on(connection, _record) -> None:  # type: ignore[no-untyped-def]
        connection.cursor().execute('PRAGMA foreign_keys=ON')

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


@pytest.fixture
async def client(
    settings: Settings, session_factory: async_sessionmaker[AsyncSession]
) -> AsyncIterator[httpx.AsyncClient]:
    async def test_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = test_db
    app.dependency_overrides[get_settings] = lambda: settings
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url='http://test') as async_client:
        yield async_client
    app.dependency_overrides.clear()


@pytest.fixture
def make_user(session_factory: async_sessionmaker[AsyncSession]) -> UserFactory:
    counter = 0

    async def factory(
        role: str = 'student', *, email: str | None = None, is_active: bool = True
    ) -> User:
        nonlocal counter
        counter += 1
        user = User(
            email=email or f'{role}{counter}@example.com',
            full_name=f'Test {role.title()} {counter}',
            role=role,
            is_active=is_active,
            hashed_password=hash_password(PASSWORD),
        )
        async with session_factory() as session:
            session.add(user)
            await session.commit()
        return user

    return factory


@pytest.fixture
def make_course(session_factory: async_sessionmaker[AsyncSession]) -> CourseFactory:
    async def factory(instructor: User, **fields: object) -> Course:
        values: dict[str, object] = {'title': 'FastAPI', 'price': 4_800_000, 'capacity': 10}
        course = Course(instructor_id=instructor.id, **(values | fields))
        async with session_factory() as session:
            session.add(course)
            await session.commit()
        return course

    return factory


@pytest.fixture
def auth(settings: Settings) -> Callable[[User], dict[str, str]]:
    """auth(user) -> {'Authorization': 'Bearer <token>'} without calling /auth/token."""

    def headers(user: User) -> dict[str, str]:
        token = create_access_token(user.id, user.role, settings)
        return {'Authorization': f'Bearer {token}'}

    return headers
