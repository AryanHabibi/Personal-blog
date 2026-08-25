import pytest


@pytest.fixture()
def category(client, admin_token):
    return client.post(
        "/categories", json={"name": "Engineering"}, headers={"Authorization": f"Bearer {admin_token}"}
    ).json()


def test_create_blog_requires_admin(client, regular_token, category):
    response = client.post(
        "/blogs",
        json={"title": "Post", "content": "body", "category_id": category["id"]},
        headers={"Authorization": f"Bearer {regular_token}"},
    )
    assert response.status_code == 403


def test_create_blog_bad_category(client, admin_token):
    response = client.post(
        "/blogs",
        json={"title": "Post", "content": "body", "category_id": 999},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 400


def test_create_blog_success(client, admin_token, category):
    response = client.post(
        "/blogs",
        json={"title": "Post", "content": "body", "category_id": category["id"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    assert response.json()["category_id"] == category["id"]


def test_get_blog_not_found(client):
    response = client.get("/blogs/999")
    assert response.status_code == 404


def test_get_blog_success(client, admin_token, category):
    blog = client.post(
        "/blogs",
        json={"title": "Post", "content": "body", "category_id": category["id"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()

    response = client.get(f"/blogs/{blog['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Post"


def test_list_blogs_pagination(client, admin_token, category):
    for i in range(3):
        client.post(
            "/blogs",
            json={"title": f"Post {i}", "content": "body", "category_id": category["id"]},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    response = client.get("/blogs", params={"page": 1, "page_size": 2})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert len(body["items"]) == 2


def test_list_blogs_search_is_case_insensitive(client, admin_token, category):
    client.post(
        "/blogs",
        json={"title": "FastAPI Deep Dive", "content": "routers and dependencies", "category_id": category["id"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    client.post(
        "/blogs",
        json={"title": "Cooking Basics", "content": "how to boil an egg", "category_id": category["id"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    response = client.get("/blogs", params={"q": "fastapi"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "FastAPI Deep Dive"


def test_update_blog_partial(client, admin_token, category):
    blog = client.post(
        "/blogs",
        json={"title": "Original", "content": "body", "category_id": category["id"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()

    response = client.put(
        f"/blogs/{blog['id']}",
        json={"title": "Updated"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Updated"
    assert body["content"] == "body"
    assert body["updated_at"] != body["created_at"]


def test_delete_blog_requires_admin(client, regular_token, admin_token, category):
    blog = client.post(
        "/blogs",
        json={"title": "Post", "content": "body", "category_id": category["id"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()

    response = client.delete(f"/blogs/{blog['id']}", headers={"Authorization": f"Bearer {regular_token}"})
    assert response.status_code == 403


def test_delete_blog_success(client, admin_token, category):
    blog = client.post(
        "/blogs",
        json={"title": "Post", "content": "body", "category_id": category["id"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()

    response = client.delete(f"/blogs/{blog['id']}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 204
    assert client.get(f"/blogs/{blog['id']}").status_code == 404
