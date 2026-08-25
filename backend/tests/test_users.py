from comments.models import Comment
from dashboard.models import Message, SavedBlog


def test_register_success(client):
    response = client.post(
        "/users/register",
        json={"email": "new@example.com", "password": "correcthorse"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new@example.com"
    assert body["is_verified"] is False
    assert "hashed_password" not in body


def test_register_duplicate_email(client, regular_user):
    response = client.post(
        "/users/register",
        json={"email": regular_user.email, "password": "correcthorse"},
    )
    assert response.status_code == 400


def test_register_short_password(client):
    response = client.post(
        "/users/register",
        json={"email": "shortpw@example.com", "password": "short"},
    )
    assert response.status_code == 422


def test_register_bad_email(client):
    response = client.post(
        "/users/register",
        json={"email": "not-an-email", "password": "correcthorse"},
    )
    assert response.status_code == 422


def test_verify_email_success(client, sent_emails):
    client.post("/users/register", json={"email": "verify@example.com", "password": "correcthorse"})
    token = sent_emails[-1]["token"]

    response = client.get(f"/users/verify?token={token}")
    assert response.status_code == 200

    login_response = client.post(
        "/users/login",
        json={"email": "verify@example.com", "password": "correcthorse"},
    )
    assert login_response.status_code == 200


def test_verify_email_invalid_token(client):
    response = client.get("/users/verify?token=garbage")
    assert response.status_code == 400


def test_verify_email_wrong_purpose_rejected(client, regular_token):
    # regular_token was minted for purpose="login", not "email_verification"
    response = client.get(f"/users/verify?token={regular_token}")
    assert response.status_code == 400


def test_login_unknown_email(client):
    response = client.post(
        "/users/login",
        json={"email": "nobody@example.com", "password": "whatever123"},
    )
    assert response.status_code == 404


def test_login_unverified(client):
    client.post("/users/register", json={"email": "unverified@example.com", "password": "correcthorse"})
    response = client.post(
        "/users/login",
        json={"email": "unverified@example.com", "password": "correcthorse"},
    )
    assert response.status_code == 403


def test_login_wrong_password(client, regular_user):
    response = client.post(
        "/users/login",
        json={"email": regular_user.email, "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_login_success(client, regular_user):
    response = client.post(
        "/users/login",
        json={"email": regular_user.email, "password": "correcthorse"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_get_me_requires_auth(client):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_get_me_success(client, regular_user, regular_token):
    response = client.get("/users/me", headers={"Authorization": f"Bearer {regular_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == regular_user.email


def test_update_me_partial(client, regular_token):
    response = client.put(
        "/users/me",
        json={"first_name": "Updated"},
        headers={"Authorization": f"Bearer {regular_token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["first_name"] == "Updated"
    assert body["last_name"] is None


def test_update_me_bio_forbidden_for_regular(client, regular_token):
    response = client.put(
        "/users/me",
        json={"bio": "I am not the admin"},
        headers={"Authorization": f"Bearer {regular_token}"},
    )
    assert response.status_code == 403


def test_update_me_bio_allowed_for_admin(client, admin_token):
    response = client.put(
        "/users/me",
        json={"bio": "Building a weblog API"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["bio"] == "Building a weblog API"


def test_get_admin_bio_public(client, admin_user):
    response = client.get("/users/admin")
    assert response.status_code == 200
    body = response.json()
    assert "email" not in body
    assert "id" not in body


def test_get_admin_bio_not_found_when_no_admin_exists(client, regular_user):
    response = client.get("/users/admin")
    assert response.status_code == 404


def test_delete_user_requires_admin(client, regular_token, admin_user):
    response = client.delete(f"/users/{admin_user.id}", headers={"Authorization": f"Bearer {regular_token}"})
    assert response.status_code == 403


def test_delete_user_blocks_admin_self_delete(client, admin_user, admin_token):
    response = client.delete(f"/users/{admin_user.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 400


def test_delete_user_not_found(client, admin_token):
    response = client.delete("/users/999", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404


def test_delete_user_cascades_their_content(client, db_session, admin_token, regular_user, regular_token):
    category = client.post(
        "/categories",
        json={"name": "Deletion Testing"},
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()
    blog = client.post(
        "/blogs",
        json={"title": "Test Blog", "content": "Body", "category_id": category["id"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()
    client.post(
        f"/blogs/{blog['id']}/comments",
        json={"content": "A comment"},
        headers={"Authorization": f"Bearer {regular_token}"},
    )
    client.post(f"/dashboard/saved-blogs/{blog['id']}", headers={"Authorization": f"Bearer {regular_token}"})
    client.post(
        "/dashboard/messages",
        json={"subject": "hi", "body": "test"},
        headers={"Authorization": f"Bearer {regular_token}"},
    )

    response = client.delete(f"/users/{regular_user.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 204

    assert db_session.query(Comment).filter(Comment.user_id == regular_user.id).count() == 0
    assert db_session.query(SavedBlog).filter(SavedBlog.user_id == regular_user.id).count() == 0
    assert db_session.query(Message).filter(Message.user_id == regular_user.id).count() == 0
