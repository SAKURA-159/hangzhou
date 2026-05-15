import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.house import House
from app.models.user import User
from app.utils.security import hash_password

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def admin_token_headers(client):
    # Create admin user
    db = TestingSessionLocal()
    user = User(
        username="admin",
        email="admin@test.com",
        hashed_password=hash_password("admin123"),
        is_admin=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    resp = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_token_headers(client):
    db = TestingSessionLocal()
    user = User(
        username="user",
        email="user@test.com",
        hashed_password=hash_password("user123"),
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    resp = client.post("/api/auth/login", json={"username": "user", "password": "user123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_houses(db):
    houses = [
        House(name="测试楼盘1", place="西湖", price=50000.0, introduction="测试", room_count=3,
              min_area=80.0, max_area=120.0, avg_area=100.0, property_type="住宅", price_flag="正常"),
        House(name="测试楼盘2", place="西湖", price=45000.0, introduction="测试", room_count=2,
              min_area=60.0, max_area=90.0, avg_area=75.0, property_type="住宅", price_flag="正常"),
        House(name="测试楼盘3", place="萧山", price=18000.0, introduction="测试", room_count=4,
              min_area=100.0, max_area=150.0, avg_area=125.0, property_type="住宅", price_flag="正常"),
        House(name="别墅1", place="西湖", price=80000.0, introduction="豪华别墅", room_count=5,
              min_area=200.0, max_area=300.0, avg_area=250.0, property_type="别墅", price_flag="正常"),
    ]
    for h in houses:
        db.add(h)
    db.commit()
    return houses
