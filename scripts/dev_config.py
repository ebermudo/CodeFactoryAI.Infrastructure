"""Shared configuration for explicit local commands; never reads Codex credentials."""

from pathlib import Path
import json
import os

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
TOOLS = ROOT / ".tools"
ENV_FILE = ROOT / ".env"


def local_values() -> dict[str, str]:
    if not ENV_FILE.exists():
        raise RuntimeError(
            "Missing Infrastructure/.env. Run setup_foundation.py or environment.py up."
        )
    values = dict(
        line.split("=", 1)
        for line in ENV_FILE.read_text(encoding="utf-8-sig").splitlines()
        if line and not line.startswith("#")
    )
    for key in ("POSTGRES_PASSWORD", "RABBITMQ_PASSWORD"):
        if not values.get(key):
            raise RuntimeError(
                f"Missing {key} in ignored .env; do not change passwords of existing volumes."
            )
    return values


def host_configuration() -> tuple[dict[str, str], Path]:
    versions = json.loads((ROOT / "toolchain.json").read_text())
    node = TOOLS / f"node-download/node-{versions['node']}-win-x64"
    env = os.environ.copy()
    env.update(
        DOTNET_ROOT=str(TOOLS / "dotnet"),
        DOTNET_CLI_HOME=str(TOOLS / "dotnet-home"),
        DOTNET_CLI_TELEMETRY_OPTOUT="1",
        NUGET_PACKAGES=str(TOOLS / "nuget"),
        NPM_CONFIG_CACHE=str(TOOLS / "npm-cache"),
        PLAYWRIGHT_BROWSERS_PATH=str(TOOLS / "playwright"),
        ASPNETCORE_ENVIRONMENT="Development",
        CODEFACTORY_API_TARGET="http://127.0.0.1:5240",
    )
    env["PATH"] = (
        str(node)
        + os.pathsep
        + str(TOOLS / "dotnet")
        + os.pathsep
        + env.get("PATH", "")
    )
    return env, node


def application_command(
    name: str, watch: bool = True, migrate: bool = False
) -> tuple[list[str], Path, dict[str, str]]:
    env, node = host_configuration()
    if name == "ui":
        cwd = WORKSPACE / "CodeFactoryAI.ClientAngular"
        script = cwd / "node_modules/@angular/cli/bin/ng.js"
        if not (node / "node.exe").exists() or not script.exists():
            raise RuntimeError(
                "Node/Angular dependencies missing; run scripts/setup_foundation.py."
            )
        return (
            [
                str(node / "node.exe"),
                str(script),
                "serve",
                "--host",
                "127.0.0.1",
                "--port",
                "4200",
            ],
            cwd,
            env,
        )
    values = local_values()
    if name == "api":
        cwd = WORKSPACE / "CodeFactoryAI.API"
        dotnet = TOOLS / "dotnet/dotnet.exe"
        if not dotnet.exists():
            raise RuntimeError(".NET SDK missing; run scripts/setup_foundation.py.")
        env["ConnectionStrings__Factory"] = (
            "Host=127.0.0.1;Port=55432;Database=codefactory;Username=factory;Password="
            + values["POSTGRES_PASSWORD"]
        )
        env["RabbitMq__ConnectionString"] = (
            "amqp://factory:" + values["RABBITMQ_PASSWORD"] + "@127.0.0.1:55672/"
        )
        if migrate:
            command = [
                str(dotnet),
                "run",
                "--project",
                "src/CodeFactoryAI.Api",
                "--no-launch-profile",
                "--",
                "--migrate",
            ]
        elif watch:
            command = [
                str(dotnet),
                "watch",
                "--non-interactive",
                "--project",
                "src/CodeFactoryAI.Api",
                "run",
                "--no-launch-profile",
                "--urls",
                "http://127.0.0.1:5240",
            ]
        else:
            command = [
                str(dotnet),
                "run",
                "--project",
                "src/CodeFactoryAI.Api",
                "--no-launch-profile",
                "--urls",
                "http://127.0.0.1:5240",
            ]
        return command, cwd, env
    if name == "runner":
        cwd = ROOT / "runner"
        token = values.get("RUNNER_SERVICE_TOKEN", "")
        if len(token) < 32:
            raise RuntimeError(
                "Runner requires RUNNER_SERVICE_TOKEN in ignored .env (32+ random characters)."
            )
        env["RUNNER_SERVICE_TOKEN"] = token
        return (
            [
                str(cwd / ".venv/Scripts/python.exe"),
                "-m",
                "uvicorn",
                "codefactory_runner.main:app_factory",
                "--factory",
                "--host",
                "127.0.0.1",
                "--port",
                "8190",
            ],
            cwd,
            env,
        )
    raise RuntimeError("Unknown service")
