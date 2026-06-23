import io

from fastapi.testclient import TestClient

from main import app
from app.services.settings import load_local_env

client = TestClient(app)


def upload(path: str, text: str):
    return client.post(path, files={"file": ("people.csv", io.BytesIO(text.encode()), "text/csv")})


def test_analyze_is_non_destructive_and_finds_issues():
    response = upload("/datasets/analyze", "id,name,email,amount\n001,Ada,bad-email,10\n001,,ada@example.com,99999\n")
    assert response.status_code == 200
    analysis = response.json()["analysis"]
    assert analysis["metadata"]["rows"] == 2
    assert any(issue["issue_type"] == "duplicate_ids" for issue in analysis["issues"])
    assert any(issue["issue_type"] == "invalid_email" for issue in analysis["issues"])


def test_clean_returns_a_downloadable_export():
    response = upload("/datasets/clean", "name,score\nAda,10\nAda,10\nBob,\n")
    assert response.status_code == 200
    body = response.json()
    assert body["export"]["download_url"].startswith("/exports/")
    download = client.get(body["export"]["download_url"])
    assert download.status_code == 200


def test_ai_insights_requires_an_explicit_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = upload("/datasets/ai-insights", "name,score\nAda,10\n")
    assert response.status_code == 503


def test_local_env_loader_does_not_replace_real_environment(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("OPENAI_API_KEY=from_file\n", encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "from_environment")
    load_local_env()
    assert __import__("os").environ["OPENAI_API_KEY"] == "from_environment"
