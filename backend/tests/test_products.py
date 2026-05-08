import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

# Use a separate test database (won't affect your real data)
TEST_DATABASE_URL = "sqlite:///./test_inventory.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the real DB with test DB
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

# ✅ TEST 1 — API is running
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Inventory API is running ✅"}

# ✅ TEST 2 — Create a product
def test_create_product():
    response = client.post("/products/", json={
        "name": "Test Laptop",
        "description": "Test Description",
        "quantity": 10,
        "price": 50000,
        "category": "Electronics"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Laptop"
    assert data["quantity"] == 10
    assert data["price"] == 50000
    assert "id" in data

# ✅ TEST 3 — Get all products
def test_get_all_products():
    response = client.get("/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# ✅ TEST 4 — Get single product
def test_get_single_product():
    # First create a product
    create = client.post("/products/", json={
        "name": "Phone",
        "quantity": 5,
        "price": 20000,
        "category": "Electronics"
    })
    product_id = create.json()["id"]

    # Then get it
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Phone"

# ✅ TEST 5 — Get product that doesn't exist
def test_get_product_not_found():
    response = client.get("/products/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

# ✅ TEST 6 — Update a product
def test_update_product():
    # Create product first
    create = client.post("/products/", json={
        "name": "Old Name",
        "quantity": 3,
        "price": 10000,
        "category": "Test"
    })
    product_id = create.json()["id"]

    # Update it
    response = client.put(f"/products/{product_id}", json={
        "name": "New Name",
        "quantity": 20
    })
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
    assert response.json()["quantity"] == 20

# ✅ TEST 7 — Delete a product
def test_delete_product():
    # Create product first
    create = client.post("/products/", json={
        "name": "To Delete",
        "quantity": 1,
        "price": 5000,
        "category": "Test"
    })
    product_id = create.json()["id"]

    # Delete it
    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 200

    # Verify it's gone
    check = client.get(f"/products/{product_id}")
    assert check.status_code == 404

# ✅ TEST 8 — Low stock alert
def test_low_stock_alert():
    # Create product with low stock
    client.post("/products/", json={
        "name": "Low Stock Item",
        "quantity": 2,
        "price": 1000,
        "category": "Test"
    })
    response = client.get("/products/alerts/low-stock")
    assert response.status_code == 200
    low_items = response.json()
    # At least one item should have quantity <= 5
    assert any(p["quantity"] <= 5 for p in low_items)