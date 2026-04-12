import pytest

@pytest.mark.asyncio
async def test_get_doe_scatter(client):
    """
    Test the GET /visualize/doe-scatter endpoint.
    Currently, this is a placeholder endpoint.
    """
    response = await client.get("/visualize/doe-scatter")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "DOE scatter plot" in data["message"]

@pytest.mark.asyncio
async def test_get_correlation_heatmap(client):
    """
    Test the GET /visualize/correlation endpoint.
    Currently, this is a placeholder endpoint.
    """
    response = await client.get("/visualize/correlation")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "Correlation heatmap" in data["message"]
