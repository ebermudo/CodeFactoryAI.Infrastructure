import secrets
from typing import Annotated
from fastapi import Depends, FastAPI, Header, HTTPException
from codefactory_runner.contracts.runner_request import RunnerRequest


def create_app(service_token: str) -> FastAPI:
    if len(service_token) < 32:
        raise ValueError("Runner requires a service token of at least 32 characters.")
    app = FastAPI(title="CodeFactoryAI Runner · disabled foundation", version="0.1.0")

    def authorize(authorization: Annotated[str | None, Header()] = None) -> None:
        if not authorization or not secrets.compare_digest(
            authorization, "Bearer " + service_token
        ):
            raise HTTPException(
                status_code=401, detail="Runner service authentication required"
            )

    @app.get("/health/live")
    def health() -> dict[str, str | bool]:
        return {"status": "foundation", "executionEnabled": False}

    @app.post("/v1/executions", dependencies=[Depends(authorize)])
    def execute(request: RunnerRequest) -> None:
        raise HTTPException(
            status_code=423,
            detail={"code": "isolation-not-validated", "attemptId": request.attemptId},
        )

    return app
