from datetime import timedelta

import pytest

from comments.models import Comment
from core.security import create_token, hash_password
from users.models import User, UserRole


@pytest.fixture()
def blog(client, admin_token):
    category = client.post(
        "/categories", json={"name": "Engineering"}, headers={"Authorization": f"Bearer {admin_token}"}
    ).json()
    return client.post(
        "/blogs",
        json={"title": "Post", "content": "body", "category_id": category["id"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()


def test_create_comment_requires_auth(client, blog):
    response = client.post(f"/blogs/{blog['id']}/comments", json={"content": "hi"})
    assert response.status_code == 401


def test_create_comment_missing_blog(client, regular_token):
    response = client.post(
        "/blogs/999/comments",
        json={"content": "hi"},
        headers={"Authorization": f"Bearer {regular_token}"},
    )
    assert response.status_code == 404


def test_create_comment_success(client, regular_token, regular_user, blog):
    response = client.post(
        f"/blogs/{blog['id']}/comments",
        json={"content": "Great post!"},
        headers={"Authorization": f"Bearer {regular_token}"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["blog_id"] == blog["id"]
    assert body["user_id"] == regular_user.id


def test_list_comments_is_public(client, regular_token, blog):
    client.post(
        f"/blogs/{blog['id']}/comments",
        json={"content": "Great post!"},
        headers={"Authorization": f"Bearer {regular_token}"},
    )

    response = client.get(f"/blogs/{blog['id']}/comments")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_delete_comment_wrong_user_forbidden(client, db_session, regular_token, blog):
    other_user = User(
        email="other@example.com",
        hashed_password=hash_password("correcthorse"),
        role=UserRole.REGULAR,
        is_verified=True,
    )
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)

    other_token = create_token({"sub": str(other_user.id)}, timedelta(minutes=60), purpose="login")

    comment = client.post(
        f"/blogs/{blog['id']}/comments",
        json={"content": "Great post!"},
        headers={"Authorization": f"Bearer {regular_token}"},
    ).json()

    response = client.delete(
        f"/comments/{comment['id']}", headers={"Authorization": f"Bearer {other_token}"}
    )
    assert response.status_code == 403


def test_delete_comment_owner_succeeds(client, regular_token, blog):
    comment = client.post(
        f"/blogs/{blog['id']}/comments",
        json={"content": "Great post!"},
        headers={"Authorization": f"Bearer {regular_token}"},
    ).json()

    response = client.delete(
        f"/comments/{comment['id']}", headers={"Authorization": f"Bearer {regular_token}"}
    )
    assert response.status_code == 204


def test_delete_comment_admin_can_delete_any(client, regular_token, admin_token, blog):
    comment = client.post(
        f"/blogs/{blog['id']}/comments",
        json={"content": "Great post!"},
        headers={"Authorization": f"Bearer {regular_token}"},
    ).json()

    response = client.delete(
        f"/comments/{comment['id']}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204


def test_delete_blog_cascades_comments(client, db_session, admin_token, regular_token, blog):
    client.post(
        f"/blogs/{blog['id']}/comments",
        json={"content": "Great post!"},
        headers={"Authorization": f"Bearer {regular_token}"},
    )

    client.delete(f"/blogs/{blog['id']}", headers={"Authorization": f"Bearer {admin_token}"})

    assert db_session.query(Comment).filter(Comment.blog_id == blog["id"]).count() == 0
