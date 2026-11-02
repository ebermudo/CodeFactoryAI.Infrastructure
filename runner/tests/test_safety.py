from fastapi.testclient import TestClient
from codefactory_runner.app import create_app


def test_runner_fails_closed_and_requires_service_identity() -> None:
    client = TestClient(create_app("t" * 40))
    payload = {
        "schemaVersion": "1.0.0",
        "attemptId": "11111111-1111-4111-8111-111111111111",
        "workspaceId": "22222222-2222-4222-8222-222222222222",
        "contextSnapshotId": "33333333-3333-4333-8333-333333333333",
        "provider": "codex",
    }
    assert client.get("/health/live").json()["executionEnabled"] is False
    assert client.post("/v1/executions", json=payload).status_code == 401
    assert (
        client.post(
            "/v1/executions",
            json=payload,
            headers={"Authorization": "Bearer " + "t" * 40},
        ).status_code
        == 423
    )
    payload["provider"] = "arbitrary-shell"
    assert (
        client.post(
            "/v1/executions",
            json=payload,
            headers={"Authorization": "Bearer " + "t" * 40},
        ).status_code
        == 422
    )
