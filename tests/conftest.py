from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from buildradar.config import Settings, get_settings
from buildradar.main import app

app.dependency_overrides[get_settings] = lambda: Settings(env="development")


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
    Bypass the lifespan entirely by setting app.state directly.

    The lifespan is responsible for two things: creating the client
    and closing it. We take over both responsibilities here:
    - Creation: app.state.llm_client = fake_llm
    - Teardown: del app.state.llm_client (prevents state bleed)

    AsyncClient with ASGITransport does NOT trigger the lifespan
    unless you pass lifespan="on" explicitly — the default is "off",
    so this is safe.
    """

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
    Simulate the branch where anthropic_api_key is absent at startup,
    which sets llm_client = None and causes /ready to return 503.
    """

    app.state.llm_client = None
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as async_client:
        yield async_client

    del app.state.llm_client
