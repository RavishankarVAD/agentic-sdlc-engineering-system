from fastapi.testclient import TestClient
from generated.url_shortener_api import app
client=TestClient(app)
def test_create_redirect_analytics():
    r=client.post("/v1/urls",json={"url":"https://example.com/path"}); assert r.status_code==201
    code=r.json()["code"]
    red=client.get(f"/{code}",follow_redirects=False); assert red.status_code==307
    a=client.get(f"/v1/urls/{code}/analytics"); assert a.status_code==200 and a.json()["clicks"]>=1
def test_invalid_url(): assert client.post("/v1/urls",json={"url":"file:///etc/passwd"}).status_code==422
def test_missing_code(): assert client.get("/missing-code",follow_redirects=False).status_code==404
