import pytest
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import blogs.models  # noqa: F401  (registers Blog on Base.metadata)
import categories.models  # noqa: F401  (registers Category on Base.metadata)
import comments.models  # noqa: F401  (registers Comment on Base.metadata)
import dashboard.models  # noqa: F401  (registers SavedBlog, Message on Base.metadata)
import users.models  # noqa: F401  (registers User on Base.metadata)
from core.security import create_token, hash_password
from database import Base, get_db
from main import app
from users.models import User, UserRole


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def sent_emails(monkeypatch):
    sent = []

    def fake_send_verification_email(to_email, token):
        sent.append({"to_email": to_email, "token": token})

    monkeypatch.setattr("users.router.send_verification_email", fake_send_verification_email)
    return sent


@pytest.fixture()
def regular_user(db_session):
    user = User(
        email="regular@example.com",
        hashed_password=hash_password("correcthorse"),
        role=UserRole.REGULAR,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def regular_token(regular_user):
    return create_token({"sub": str(regular_user.id)}, timedelta(minutes=60), purpose="login")


@pytest.fixture()
def admin_user(db_session):
    user = User(
        email="admin@example.com",
        hashed_password=hash_password("correcthorse"),
        role=UserRole.ADMIN,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def admin_token(admin_user):
    return create_token({"sub": str(admin_user.id)}, timedelta(minutes=60), purpose="login")
