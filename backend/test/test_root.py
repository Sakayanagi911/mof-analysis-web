import pytest

@pytest.mark.asyncio
async def test_read_root(client):
    """
    Test the GET / endpoint for basic connectivity and version info.
    """
    response = await client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "MOF Analysis API" in data["message"]
    assert data["version"] == "1.0.0"
