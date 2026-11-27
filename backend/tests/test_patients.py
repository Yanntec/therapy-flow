def _create_patient(client, headers, name="Max Muster"):
    r = client.post(
        "/patients",
        json={"name": name, "geburtsdatum": "01.01.1990"},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    return r.json()


def test_create_and_list_patients(client, user_headers):
    _create_patient(client, user_headers)
    r = client.get("/patients", headers=user_headers)
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_patients_are_isolated_between_users(client, user_headers, other_user_headers):
    _create_patient(client, user_headers)
    r = client.get("/patients", headers=other_user_headers)
    assert r.json() == []


def test_other_user_cannot_access_patient_endpoints(client, user_headers, other_user_headers):
    p = _create_patient(client, user_headers)
    pid, qr = p["id"], p["qr_code"]

    assert client.get(f"/generate-doc/{pid}", headers=other_user_headers).status_code == 404
    assert client.get(f"/patients/{pid}/qr-image", headers=other_user_headers).status_code == 404
    assert client.post(f"/patients/{pid}/regenerate-qr", headers=other_user_headers).status_code == 404
    assert client.get(f"/patient-by-qr/{qr}", headers=other_user_headers).status_code == 404


def test_other_user_cannot_create_session_for_foreign_patient(client, user_headers, other_user_headers):
    pid = _create_patient(client, user_headers)["id"]
    r = client.post(
        "/sessions",
        json={"patient_id": pid, "therapeut_id": "t1", "tags": [], "freitext": "x"},
        headers=other_user_headers,
    )
    assert r.status_code == 404


def test_create_session_and_generate_doc(client, user_headers):
    pid = _create_patient(client, user_headers)["id"]
    r = client.post(
        "/sessions",
        json={
            "patient_id": pid,
            "therapeut_id": "t1",
            "tags": ["#Motorik"],
            "freitext": "Gute Einheit",
        },
        headers=user_headers,
    )
    assert r.status_code == 200
    assert r.json()["status"] == "success"

    doc = client.get(f"/generate-doc/{pid}", headers=user_headers)
    assert doc.status_code == 200
    assert doc.content[:2] == b"PK"  # .docx ist ein ZIP


def test_regenerate_qr_changes_code(client, user_headers):
    p = _create_patient(client, user_headers)
    r = client.post(f"/patients/{p['id']}/regenerate-qr", headers=user_headers)
    assert r.status_code == 200
    assert r.json()["qr_code"] != p["qr_code"]


def test_qr_image_is_png(client, user_headers):
    pid = _create_patient(client, user_headers)["id"]
    r = client.get(f"/patients/{pid}/qr-image", headers=user_headers)
    assert r.status_code == 200
    assert r.content[:8] == b"\x89PNG\r\n\x1a\n"