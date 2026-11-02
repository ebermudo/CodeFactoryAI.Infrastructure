"""Explicit Foundation setup; installs only repository-local tools/environments."""
from pathlib import Path
import json
import os
import secrets
import subprocess
import sys
import venv

root=Path(__file__).resolve().parents[1]
workspace=root.parent
subprocess.run([sys.executable,str(root/"scripts/bootstrap_tools.py")],check=True)
versions=json.loads((root/"toolchain.json").read_text())
tools=root/".tools"
node=tools/f"node-download/node-{versions['node']}-win-x64"
env=os.environ.copy()
env.update(DOTNET_ROOT=str(tools/"dotnet"),DOTNET_CLI_HOME=str(tools/"dotnet-home"),DOTNET_CLI_TELEMETRY_OPTOUT="1",NUGET_PACKAGES=str(tools/"nuget"),NPM_CONFIG_CACHE=str(tools/"npm-cache"),PIP_CACHE_DIR=str(tools/"pip-cache"),PLAYWRIGHT_BROWSERS_PATH=str(tools/"playwright"))
env["PATH"]=str(node)+os.pathsep+str(tools/"dotnet")+os.pathsep+env.get("PATH","")
for project,lock in [(workspace/"CodeFactoryAI.Agents","requirements-test.lock.txt"),(root/"runner","requirements-test.lock.txt")]:
    py=project/".venv/Scripts/python.exe"
    if not py.exists():
        venv.EnvBuilder(with_pip=True).create(project/".venv")
    subprocess.run([str(py),"-m","pip","install","-r",str(project/lock)],env=env,check=True)
    subprocess.run([str(py),"-m","pip","install","--no-deps","-e",str(project)],env=env,check=True)
client=workspace/"CodeFactoryAI.ClientAngular"
subprocess.run([str(node/"node.exe"),str(node/"node_modules/npm/bin/npm-cli.js"),"ci","--no-audit","--no-fund"],cwd=client,env=env,check=True)
subprocess.run([str(node/"node.exe"),str(client/"node_modules/@playwright/test/cli.js"),"install","chromium"],env=env,check=True)
ef=tools/"dotnet-tools/dotnet-ef.exe"
if not ef.exists():
    subprocess.run([str(tools/"dotnet/dotnet.exe"),"tool","install","dotnet-ef","--version","10.0.14","--tool-path",str(ef.parent)],env=env,check=True)
env_file=root/".env"
existing = env_file.read_text(encoding="utf-8") if env_file.exists() else ""
known = {line.split("=",1)[0] for line in existing.splitlines() if line and not line.startswith("#")}
additions = "".join(f"{name}=Aa1!{secrets.token_hex(32)}\n" for name in ["POSTGRES_PASSWORD","RABBITMQ_PASSWORD","RUNNER_SERVICE_TOKEN","BRAIN_BOOTSTRAP_PASSWORD"] if name not in known)
if additions:
    env_file.write_text(existing.rstrip() + ("\n" if existing else "") + additions,encoding="utf-8")
print("Foundation dependencies ready. Start Compose explicitly; no application or Codex execution has been started.")
