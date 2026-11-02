async def test_crud_flow(client):
    r = await client.post("/items", json={"name": "first", "description": "d"})
    assert r.status_code == 201
    item = r.json()
    assert item["name"] == "first"

    r = await client.get(f"/items/{item['id']}")
    assert r.status_code == 200

    r = await client.patch(f"/items/{item['id']}", json={"name": "renamed"})
    assert r.json()["name"] == "renamed"
    assert r.json()["description"] == "d"

    r = await client.get("/items")
    assert [i["id"] for i in r.json()] == [item["id"]]

    r = await client.delete(f"/items/{item['id']}")
    assert r.status_code == 204
    assert (await client.get(f"/items/{item['id']}")).status_code == 404


async def test_list_limit_offset(client):
    for n in range(3):
        await client.post("/items", json={"name": f"i{n}"})
    r = await client.get("/items", params={"limit": 1, "offset": 1})
    assert [i["name"] for i in r.json()] == ["i1"]


async def test_not_found_error_format(client):
    r = await client.get("/items/999999")
    assert r.status_code == 404
    assert r.json() == {"error": {"code": "not_found", "message": "Item не найден"}}


async def test_validation_error_format(client):
    r = await client.post("/items", json={"name": ""})
    assert r.status_code == 422
    body = r.json()
    assert body["error"]["code"] == "validation_error"
    assert "name" in body["error"]["message"]


async def test_unhandled_error_format(client, monkeypatch):
    from app.services.item import ItemService

    async def boom(*_a, **_k):
        raise RuntimeError("secret internals")

    monkeypatch.setattr(ItemService, "list", boom)
    r = await client.get("/items")
    assert r.status_code == 500
    assert r.json() == {"error": {"code": "internal_error", "message": "Внутренняя ошибка сервера"}}
