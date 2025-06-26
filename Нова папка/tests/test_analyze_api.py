from fastapi.testclient import TestClient
from backend.app import app, news_store
from config import STUDENT_ID

client = TestClient(app)

def test_analyze_empty():
    news_store[STUDENT_ID] = []
    res = client.post(f"/analyze/{STUDENT_ID}")
    assert res.status_code == 200
    assert res.json() == {"analyzed": 0, "articles": []}

def test_analyze_real(monkeypatch):
    from backend import app as backend_app  # доступ до модуля, щоб патчити analyzer

    news_store[STUDENT_ID] = [
        {"title": "I love this", "link": "u1", "published": ""},
        {"title": "I hate that", "link": "u2", "published": ""}
    ]

    class FakeAnalyzer:
        @staticmethod
        def polarity_scores(txt):
            if "love" in txt:
                return {"neg": 0.0, "neu": 0.3, "pos": 0.7, "compound": 0.8}
            else:
                return {"neg": 0.6, "neu": 0.4, "pos": 0.0, "compound": -0.6}

    # Підміна існуючого аналізатора
    monkeypatch.setattr(backend_app, "analyzer", FakeAnalyzer())

    res = client.post(f"/analyze/{STUDENT_ID}")
    assert res.status_code == 200
    data = res.json()
    assert data["analyzed"] == 2
    arts = data["articles"]
    assert arts[0]["sentiment"] == "positive"
    assert arts[1]["sentiment"] == "negative"
    assert "compound" in arts[0]["scores"]
