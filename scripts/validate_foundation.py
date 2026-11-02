"""Run real Foundation checks. Services must be started explicitly beforehand."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import time

root = Path(__file__).resolve().parents[1]
workspace = root.parent
tools = root / ".tools"
versions = json.loads((root / "toolchain.json").read_text())
node_dir = tools / f"node-download/node-{versions['node']}-win-x64"
dotnet = tools / "dotnet/dotnet.exe"
agents = workspace / "CodeFactoryAI.Agents"
client = workspace / "CodeFactoryAI.ClientAngular"
py_agents = agents / ".venv/Scripts/python.exe"
py_runner = root / "runner/.venv/Scripts/python.exe"
node = node_dir / "node.exe"
env = os.environ.copy()
env.update(DOTNET_ROOT=str(tools/"dotnet"), DOTNET_CLI_HOME=str(tools/"dotnet-home"), DOTNET_CLI_TELEMETRY_OPTOUT="1", NUGET_PACKAGES=str(tools/"nuget"), NPM_CONFIG_CACHE=str(tools/"npm-cache"), PLAYWRIGHT_BROWSERS_PATH=str(tools/"playwright"))
env["PATH"] = str(node_dir) + os.pathsep + str(tools/"dotnet") + os.pathsep + env.get("PATH", "")
local = dict(line.split("=",1) for line in (root/".env").read_text().splitlines() if line and not line.startswith("#"))
env["FACTORY_TEST_CONNECTION"] = "Host=127.0.0.1;Port=55432;Database=codefactory;Username=factory;Password=" + local["POSTGRES_PASSWORD"]
output = root / "artifacts/local/validation"
output.mkdir(parents=True, exist_ok=True)
sln = workspace / "CodeFactoryAI.API/CodeFactoryAI.slnx"
ng = client / "node_modules/@angular/cli/bin/ng.js"
commands = [
    ("contracts-drift", [str(py_agents), str(workspace/"CodeFactoryAI.API/scripts/generate_contracts.py"), "--check"], workspace),
    ("dotnet-restore-locked", [str(dotnet),"restore",str(sln),"--locked-mode"], workspace),
    ("dotnet-build", [str(dotnet),"build",str(sln),"-c","Release","--no-restore"], workspace),
    ("dotnet-tests", [str(dotnet),"test",str(sln),"-c","Release","--no-build","--no-restore","--logger","trx;LogFileName=foundation.trx","--results-directory",str(output/"dotnet")], workspace),
    ("agents-tests", [str(py_agents),"-m","pytest",str(agents/"tests"),"-q","--junitxml",str(output/"agents.xml")], agents),
    ("python-lint", [str(py_agents),"-m","ruff","check",str(agents/"src"),str(agents/"tests"),str(root/"runner/src"),str(root/"runner/tests"),str(root/"tests")], workspace),
    ("python-types", [str(py_agents),"-m","mypy","--config-file",str(agents/"pyproject.toml"),str(agents/"src")], workspace),
    ("runner-tests", [str(py_runner),"-m","pytest",str(root/"runner/tests"),"-q","--junitxml",str(output/"runner.xml")], root/"runner"),
    ("compose-config", ["docker","compose","--env-file",str(root/".env"),"-f",str(root/"compose.yaml"),"config","--quiet"], root),
    ("services-integration", [str(py_runner),"-m","pytest",str(root/"tests"),"-q","--junitxml",str(output/"services.xml")], root),
    ("services-persistence", [str(py_runner),str(root/"scripts/test_persistence.py")], root),
    ("angular-types", [str(node),str(client/"node_modules/typescript/bin/tsc"),"-p","tsconfig.contracts.json"], client),
    ("angular-build", [str(node),str(ng),"build"], client),
    ("angular-unit", [str(node),str(client/"node_modules/vitest/vitest.mjs"),"run"], client),
    ("angular-contracts", [str(node),"--test","tests/contracts.test.mjs"], client),
    ("angular-e2e", [str(node),str(client/"node_modules/@playwright/test/cli.js"),"test"], client),
]
results=[]
for name, command, cwd in commands:
    started=time.monotonic()
    log=output/(name+".log")
    with log.open("w",encoding="utf-8") as stream:
        result=subprocess.run(command,cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=240,check=False)
    results.append({"name":name,"exitCode":result.returncode,"durationSeconds":round(time.monotonic()-started,2),"logSha256":hashlib.sha256(log.read_bytes()).hexdigest()})
    print(f"{name}: {'PASS' if result.returncode == 0 else 'FAIL'}",flush=True)
    if result.returncode:
        print(log.read_text(encoding="utf-8",errors="replace")[-5000:])
        break
report={"phase":"1-foundation","timestampUtc":datetime.now(timezone.utc).isoformat(),"autonomousExecutionEnabled":False,"results":results}
(output/"summary.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
raise SystemExit(0 if len(results)==len(commands) and all(r["exitCode"]==0 for r in results) else 1)
