"""Explicit local launch commands. Never starts Codex or generated code."""
from pathlib import Path
import json
import os
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
workspace = root.parent
tools = root / ".tools"
versions = json.loads((root / "toolchain.json").read_text())
node = tools / f"node-download/node-{versions['node']}-win-x64"
env = os.environ.copy()
env.update(DOTNET_ROOT=str(tools / "dotnet"), DOTNET_CLI_HOME=str(tools / "dotnet-home"), DOTNET_CLI_TELEMETRY_OPTOUT="1", NUGET_PACKAGES=str(tools / "nuget"), NPM_CONFIG_CACHE=str(tools / "npm-cache"), PLAYWRIGHT_BROWSERS_PATH=str(tools / "playwright"))
env["PATH"] = str(node) + os.pathsep + str(tools / "dotnet") + os.pathsep + env.get("PATH", "")
values = {}
env_file = root / ".env"
if env_file.exists():
    values = dict(line.split("=",1) for line in env_file.read_text().splitlines() if line and not line.startswith("#"))
option = sys.argv[1] if len(sys.argv) == 2 else ""
if option == "ui":
    cwd = workspace / "CodeFactoryAI.ClientAngular"
    command = [str(node / "node.exe"), str(cwd / "node_modules/@angular/cli/bin/ng.js"), "serve", "--host", "127.0.0.1", "--port", "4200"]
elif option == "api":
    cwd = workspace / "CodeFactoryAI.API"
    if "POSTGRES_PASSWORD" not in values:
        raise SystemExit("Create local .env first; see README.")
    env["ConnectionStrings__Factory"] = "Host=127.0.0.1;Port=55432;Database=codefactory;Username=factory;Password=" + values["POSTGRES_PASSWORD"]
    command = [str(tools / "dotnet/dotnet.exe"), "run", "--project", "src/CodeFactoryAI.Api", "--no-launch-profile", "--urls", "http://127.0.0.1:5240"]
elif option == "runner":
    cwd = root / "runner"
    if "RUNNER_SERVICE_TOKEN" not in values:
        raise SystemExit("Create RUNNER_SERVICE_TOKEN in ignored .env; use at least 32 random characters.")
    env["RUNNER_SERVICE_TOKEN"] = values["RUNNER_SERVICE_TOKEN"]
    command = [str(cwd / ".venv/Scripts/python.exe"), "-m", "uvicorn", "codefactory_runner.main:app_factory", "--factory", "--host", "127.0.0.1", "--port", "8190"]
else:
    raise SystemExit("Usage: python scripts/dev.py ui|api|runner")
raise SystemExit(subprocess.call(command, cwd=cwd, env=env))
