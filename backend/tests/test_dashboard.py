import pytest

from dashboard.models import Message


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


def test_save_blog_requires_regular_role(client, admin_token, blog):
    response = client.post(
        f"/dashboard/saved-blogs/{blog['id']}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 403


def test_save_blog_missing_blog(client, regular_token):
    response = client.post(
        "/dashboard/saved-blogs/999", headers={"Authorization": f"Bearer {regular_token}"}
    )
    assert response.status_code == 404


def test_save_blog_success_then_duplicate(client, regular_token, blog):
    first = client.post(
        f"/dashboard/saved-blogs/{blog['id']}", headers={"Authorization": f"Bearer {regular_token}"}
    )
    assert first.status_code == 201

    second = client.post(
        f"/dashboard/saved-blogs/{blog['id']}", headers={"Authorization": f"Bearer {regular_token}"}
    )
    assert second.status_code == 400


def test_list_saved_blogs_is_scoped_to_self(client, regular_token, blog):
    client.post(f"/dashboard/saved-blogs/{blog['id']}", headers={"Authorization": f"Bearer {regular_token}"})

    response = client.get("/dashboard/saved-blogs", headers={"Authorization": f"Bearer {regular_token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_unsave_blog(client, regular_token, blog):
    client.post(f"/dashboard/saved-blogs/{blog['id']}", headers={"Authorization": f"Bearer {regular_token}"})

    response = client.delete(
        f"/dashboard/saved-blogs/{blog['id']}", headers={"Authorization": f"Bearer {regular_token}"}
    )
    assert response.status_code == 204

    again = client.delete(
        f"/dashboard/saved-blogs/{blog['id']}", headers={"Authorization": f"Bearer {regular_token}"}
    )
    assert again.status_code == 404


def test_create_message_with_blog(client, regular_token, blog):
    response = client.post(
        "/dashboard/messages",
        json={"subject": "hi", "body": "test", "blog_id": blog["id"]},
        headers={"Authorization": f"Bearer {regular_token}"},
    )
    assert response.status_code == 201
    assert response.json()["blog_id"] == blog["id"]


def test_create_message_without_blog(client, regular_token):
    response = client.post(
        "/dashboard/messages",
        json={"subject": "hi", "body": "test"},
        headers={"Authorization": f"Bearer {regular_token}"},
    )
    assert response.status_code == 201
    assert response.json()["blog_id"] is None


def test_create_message_bad_blog_id(client, regular_token):
    response = client.post(
        "/dashboard/messages",
        json={"subject": "hi", "body": "test", "blog_id": 999},
        headers={"Authorization": f"Bearer {regular_token}"},
    )
    assert response.status_code == 400


def test_message_inbox_is_admin_only(client, regular_token):
    response = client.get("/dashboard/messages", headers={"Authorization": f"Bearer {regular_token}"})
    assert response.status_code == 403


def test_message_inbox_readable_by_admin(client, admin_token, regular_token):
    client.post(
        "/dashboard/messages",
        json={"subject": "hi", "body": "test"},
        headers={"Authorization": f"Bearer {regular_token}"},
    )

    response = client.get("/dashboard/messages", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_deleting_blog_nulls_message_reference(client, db_session, admin_token, regular_token, blog):
    client.post(
        "/dashboard/messages",
        json={"subject": "hi", "body": "test", "blog_id": blog["id"]},
        headers={"Authorization": f"Bearer {regular_token}"},
    )

    client.delete(f"/blogs/{blog['id']}", headers={"Authorization": f"Bearer {admin_token}"})

    message = db_session.query(Message).first()
    assert message is not None
    assert message.blog_id is None
