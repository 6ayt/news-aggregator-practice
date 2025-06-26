from fastapi.testclient import TestClient
from backend.app import app, store, news_store, sources_store
from config import STUDENT_ID

client = TestClient(app)

def clear_test_data():
    store[STUDENT_ID] = []
    news_store[STUDENT_ID] = []
    sources_store[STUDENT_ID] = []

def test_get_empty_sources():
    clear_test_data()
    res = client.get(f"/sources/{STUDENT_ID}")
    assert res.status_code == 200
    assert res.json() == {"sources": []}

def test_add_and_get_source():
    store[STUDENT_ID] = []  # очищаємо перед тестом

    url = "https://example.com/rss"
    res1 = client.post(f"/sources/{STUDENT_ID}", json={"url": url})
    assert res1.status_code == 200
    assert url in res1.json()["sources"]

    res2 = client.get(f"/sources/{STUDENT_ID}")
    assert res2.status_code == 200
    assert res2.json()["sources"] == [url]

