import io

from fastapi.testclient import TestClient

from main import app

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
