import pytest
from httpx import AsyncClient
from structlog import getLogger

log = getLogger()


@pytest.mark.api
async def test_get_healthiness_returns_200(
    client: AsyncClient,
) -> None:
    """GET /health return 200"""
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.api
async def test_readiness_returns_200_when_llm_is_available(
    client: AsyncClient,
) -> None:
    """GET /ready returns 200 when the LLM client initialised successfully."""
    response = await client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


@pytest.mark.api
async def test_readiness_returns_503_when_llm_is_unavailable(
    client_without_llm: AsyncClient,
) -> None:
    """
    GET /ready returns 503 when anthropic_api_key was absent at startup,
    leaving app.state.llm_client = None.
    """
    response = await client_without_llm.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "message": "LLM client is unavailable",
            "code": "llm_unavailable",
            "details": {},
        }
    }
