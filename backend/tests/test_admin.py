def test_admin_routes_forbidden_for_normal_user(client, user_headers):
    assert client.get("/admin/users", headers=user_headers).status_code in (401, 403)
    assert client.get("/admin/test", headers=user_headers).status_code in (401, 403)


def test_admin_can_list_users(client, admin_headers):
    r = client.get("/admin/users", headers=admin_headers)
    assert r.status_code == 200
    assert any(u["email"] == "admin@example.com" for u in r.json())


def test_admin_cannot_deactivate_self(client, admin_headers):
    me = client.get("/me", headers=admin_headers).json()
    r = client.patch(
        f"/admin/users/{me['id']}/status",
        json={"is_active": False},
        headers=admin_headers,
    )
    assert r.status_code == 400


def test_admin_cannot_remove_own_admin_role(client, admin_headers):
    me = client.get("/me", headers=admin_headers).json()
    r = client.patch(
        f"/admin/users/{me['id']}/role",
        json={"is_admin": False},
        headers=admin_headers,
    )
    assert r.status_code == 400


def test_admin_can_deactivate_other_user(client, admin_headers, user_headers):
    users = client.get("/admin/users", headers=admin_headers).json()
    target = next(u for u in users if u["email"] == "user@example.com")
    r = client.patch(
        f"/admin/users/{target['id']}/status",
        json={"is_active": False},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.json()["is_active"] is False


def test_unknown_user_returns_404(client, admin_headers):
    assert client.get("/admin/users/9999", headers=admin_headers).status_code == 404