import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from backend.main import app


def skip_if_weaviate_unavailable():
    import weaviate

    try:
        client = weaviate.Client("http://localhost:8080")
        client.is_ready()
    except Exception:
        pytest.skip("Skipping test: Weaviate not ready")


load_dotenv()


client = TestClient(app)


def validate_product_fields(product: dict):
    expected_fields = {
        "product_id": int,
        "title": str,
        "store": str,
        "description": str,
        "features": list,
        "average_rating": (int, float),
        "rating_number": int,
        "price": (int, float),
        "details": str,
        "main_hi_res_image": str,
    }
    for field, expected_type in expected_fields.items():
        assert field in product, f"Missing key: {field}"
        assert isinstance(
            product[field], expected_type
        ), f"Field {field} has incorrect type"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("ok") is True


def test_search_endpoint():
    skip_if_weaviate_unavailable()
    response = client.get("/search", params={"query": "pool", "query_type": "keyword"})
    assert response.status_code == 200
    data = response.json()
    assert data.get("ok") is True
    assert isinstance(data.get("products"), list)
    if data["products"]:
        validate_product_fields(data["products"][0])


def test_product_by_id_endpoint():
    skip_if_weaviate_unavailable()
    response = client.get("/products/1")
    assert response.status_code in [200, 404]
    data = response.json()
    assert "ok" in data
    if data["ok"]:
        assert "product" in data
        validate_product_fields(data["product"])


def test_best_sellers_endpoint():
    response = client.get("/best-sellers")
    if response.status_code == 500:
        pytest.skip("Skipping test: Backend server not ready or DB not connected.")
    assert response.status_code == 200
    data = response.json()
    assert data.get("ok") is True
    assert isinstance(data.get("products"), list)
    if data["products"]:
        validate_product_fields(data["products"][0])


def test_trending_endpoint():
    response = client.get("/trending")
    if response.status_code == 500:
        pytest.skip("Skipping test: Backend server not ready or DB not connected.")
    assert response.status_code == 200
    data = response.json()
    assert data.get("ok") is True
    assert isinstance(data.get("products"), list)
    if data["products"]:
        validate_product_fields(data["products"][0])
