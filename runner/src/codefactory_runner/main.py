import os

from fastapi import FastAPI

from codefactory_runner.app import create_app


def app_factory() -> FastAPI:
    return create_app(os.environ["RUNNER_SERVICE_TOKEN"])
