import pytest
from httpx import AsyncClient
from structlog import getLogger

log = getLogger()


@pytest.mark.api
async def test_get_health_returns_200(
    client: AsyncClient,
) -> None:
    """GET /health return 200"""
    response = await client.get("/health")

    log.info(response.text)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.api
async def test_readiness_returns_200_when_llm_is_available(
    client: AsyncClient,
) -> None:
    """GET /health return 200"""
    response = await client.get("/ready")

    log.info(response.text)
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


@pytest.mark.api
async def test_readiness_returns_503_when_llm_is_unavailable(
    client_without_llm: AsyncClient,
) -> None:
    """GET /health return 200"""
    response = await client_without_llm.get("/ready")

    log.error(response.text)
    assert response.status_code == 503
