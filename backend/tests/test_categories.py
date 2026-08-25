def test_list_categories_anonymous(client):
    response = client.get("/categories")
    assert response.status_code == 200
    assert response.json() == []


def test_create_category_requires_auth(client):
    response = client.post("/categories", json={"name": "Tech"})
    assert response.status_code == 401


def test_create_category_forbidden_for_regular(client, regular_token):
    response = client.post(
        "/categories",
        json={"name": "Tech"},
        headers={"Authorization": f"Bearer {regular_token}"},
    )
    assert response.status_code == 403


def test_create_category_success(client, admin_token):
    response = client.post(
        "/categories",
        json={"name": "Tech"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Tech"


def test_create_category_duplicate_name(client, admin_token):
    client.post("/categories", json={"name": "Tech"}, headers={"Authorization": f"Bearer {admin_token}"})
    response = client.post(
        "/categories",
        json={"name": "Tech"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 400


def test_delete_category_not_found(client, admin_token):
    response = client.delete("/categories/999", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404


def test_delete_category_blocked_when_blogs_exist(client, admin_token):
    category = client.post(
        "/categories", json={"name": "Tech"}, headers={"Authorization": f"Bearer {admin_token}"}
    ).json()
    client.post(
        "/blogs",
        json={"title": "A post", "content": "body", "category_id": category["id"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    response = client.delete(f"/categories/{category['id']}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 400


def test_delete_category_succeeds_once_empty(client, admin_token):
    category = client.post(
        "/categories", json={"name": "Tech"}, headers={"Authorization": f"Bearer {admin_token}"}
    ).json()

    response = client.delete(f"/categories/{category['id']}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 204
