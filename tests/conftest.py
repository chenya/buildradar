from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from buildradar.main import create_app


class FakeAsyncAnthropic:
    """
    Fake drop-in for AsyncAnthropic that never touches the network.

    Mirrors the interface the app actually uses — close() is the
    minimum required by the lifespan teardown if it ever runs.
    Extend with fake .messages.create() etc. as your endpoints need them.
    """

    def __init__(self) -> None:
        self.closed: bool = False

    async def close(self) -> None:
        self.closed = True


@pytest.fixture
def fake_llm() -> FakeAsyncAnthropic:
    return FakeAsyncAnthropic()


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """
    Provide an async HTTP client pointed at a fresh application instance.

    A new app is created per test to guarantee complete state isolation.
    Each test sees a clean slate with no shared mutable state.
    """
    app = create_app()
    app.state.llm_client = fake_llm
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as async_client:
        yield async_client

    del app.state.llm_client


@pytest.fixture
async def client_without_llm() -> AsyncIterator[AsyncClient]:
    """
    Provide an async HTTP client pointed at a fresh application instance.

    A new app is created per test to guarantee complete state isolation.
    Each test sees a clean slate with no shared mutable state.
    """
    app = create_app()
    app.state.llm_client = None
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as async_client:
        yield async_client

    del app.state.llm_client
