"""One command for Docker or detached Windows host development."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

from dev_config import ENV_FILE, ROOT, WORKSPACE, application_command
from host_process import identity, stop_owned

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

LOGS = ROOT / "artifacts/local/environment"
STATE = LOGS / "state.json"
COMPOSE = [
    "docker",
    "compose",
    "--env-file",
    str(ENV_FILE),
    "-f",
    str(ROOT / "compose.yaml"),
]
API = "http://127.0.0.1:5240"
UI = "http://127.0.0.1:4200"


def run(command: list[str], **options: object) -> None:
    subprocess.run(command, check=True, **options)


def load_state() -> dict:
    return (
        json.loads(STATE.read_text())
        if STATE.exists()
        else {"mode": "docker", "processes": {}}
    )


def ensure_environment(create: bool = False) -> None:
    if not ENV_FILE.exists() and not create:
        raise RuntimeError("Missing .env; run environment.py up first.")
    if not ENV_FILE.exists():
        ENV_FILE.write_text(
            "".join(
                f"{key}={secrets.token_hex(32)}\n"
                for key in ["POSTGRES_PASSWORD", "RABBITMQ_PASSWORD"]
            ),
            encoding="utf-8",
        )
        print("Created ignored .env with random local infrastructure secrets.")
    for name in [
        "CodeFactoryAI.API",
        "CodeFactoryAI.ClientAngular",
        "CodeFactoryAI.Infrastructure",
        "CodeFactoryAI.Agents",
    ]:
        repo = WORKSPACE / name
        actual = Path(
            subprocess.check_output(
                ["git", "-C", str(repo), "rev-parse", "--show-toplevel"], text=True
            ).strip()
        ).resolve()
        if actual != repo.resolve():
            raise RuntimeError(f"Unexpected repository root: {repo}")
    if (
        subprocess.check_output(
            ["docker", "info", "--format", "{{.OSType}}"], text=True
        ).strip()
        != "linux"
    ):
        raise RuntimeError("Docker Desktop must use Linux containers.")
    run(COMPOSE + ["config", "--quiet"])


def port_open(port: int) -> bool:
    with socket.socket() as client:
        client.settimeout(0.5)
        return client.connect_ex(("127.0.0.1", port)) == 0


def stop_host() -> None:
    state = load_state()
    for record in state.get("processes", {}).values():
        stop_owned(record)
    state["processes"] = {}
    STATE.write_text(json.dumps(state, indent=2))


def require_free_ports(allow_docker: bool = False) -> None:
    managed_ports = set()
    if allow_docker:
        output = subprocess.check_output(
            COMPOSE + ["ps", "--format", "json"], text=True
        )
        for line in output.splitlines():
            service = json.loads(line)
            if service.get("Service") in ("api", "client"):
                managed_ports.update(
                    p["PublishedPort"] for p in service.get("Publishers", []) or []
                )
    for port in (4200, 5240):
        if port_open(port) and port not in managed_ports:
            raise RuntimeError(
                f"Port {port} is already used by an unmanaged process. Stop its terminal/server first; diagnose with environment.py status."
            )


def http(url: str, origin: str | None = None) -> tuple[int, bytes, dict]:
    request = urllib.request.Request(url, headers={"Origin": origin} if origin else {})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, response.read(), dict(response.headers)
    except urllib.error.HTTPError as error:
        return error.code, error.read(), dict(error.headers)


def verify(timeout: int = 180) -> dict:
    deadline = time.monotonic() + timeout
    last = "not ready"
    while True:
        try:
            code, body, _ = http(API + "/health/ready")
            ready = json.loads(body)
            if code != 200 or ready.get("dependencies") != {
                "postgres": "healthy",
                "rabbitmq": "healthy",
            }:
                raise RuntimeError(f"API readiness: HTTP {code}, {ready}")
            code, body, _ = http(UI + "/factory")
            if code != 200 or b"app-root" not in body:
                raise RuntimeError(f"Frontend not ready (HTTP {code})")
            code, body, _ = http(UI + "/api/v1/system-health")
            if (
                code != 200
                or json.loads(body).get("autonomousExecutionEnabled") is not False
            ):
                raise RuntimeError(f"Angular-to-API proxy failed (HTTP {code})")
            code, _, _ = http(UI + "/api/v1/projects")
            if code != 401:
                raise RuntimeError(
                    f"Protected project route must return 401, got {code}"
                )
            code, _, headers = http(API + "/api/v1/system-health", UI)
            if code != 200 or headers.get("Access-Control-Allow-Origin") != UI:
                raise RuntimeError("Explicit local CORS origin failed")
            _, _, headers = http(
                API + "/api/v1/system-health", "https://untrusted.invalid"
            )
            if "Access-Control-Allow-Origin" in headers:
                raise RuntimeError("Unexpected CORS permission for external origin")
            result = {
                "timestampUtc": datetime.now(timezone.utc).isoformat(),
                "frontend": UI,
                "api": API,
                "dependencies": ready["dependencies"],
                "proxyHttp": 200,
                "projectsHttp": 401,
                "corsAllowed": UI,
                "corsExternalRejected": True,
                "autonomousExecutionEnabled": False,
            }
            (LOGS / "checks.json").write_text(json.dumps(result, indent=2) + "\n")
            return result
        except (OSError, ValueError, RuntimeError) as error:
            last = str(error)
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    f"Startup health timeout: {last}. Logs: {LOGS}; environment.py logs"
                )
            time.sleep(1)


def start_host() -> None:
    run(COMPOSE + ["stop", "api", "client"])
    stop_host()
    require_free_ports()
    run(
        COMPOSE
        + ["up", "-d", "--wait", "--wait-timeout", "180", "postgres", "rabbitmq"]
    )
    command, cwd, env = application_command("api", migrate=True)
    with (LOGS / "migrations.log").open("w", encoding="utf-8") as stream:
        run(
            command,
            cwd=cwd,
            env=env,
            stdout=stream,
            stderr=subprocess.STDOUT,
            timeout=180,
        )
    state = {"mode": "host", "processes": {}}
    STATE.write_text(json.dumps(state))
    try:
        for name in ("api", "ui"):
            # Validate commands before detaching; children survive the launcher, not user terminals.
            application_command(name)
            with (LOGS / (name + ".log")).open("w", encoding="utf-8") as stream:
                process = subprocess.Popen(
                    [sys.executable, str(ROOT / "scripts/dev.py"), name],
                    cwd=WORKSPACE,
                    stdin=subprocess.DEVNULL,
                    stdout=stream,
                    stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                    | subprocess.CREATE_NO_WINDOW,
                    close_fds=True,
                )
            created = identity(process.pid)
            if created is None:
                raise RuntimeError(f"Could not register {name}; inspect {name}.log")
            state["processes"][name] = {"pid": process.pid, "creationTime": created}
            STATE.write_text(json.dumps(state, indent=2))
        verify()
    except BaseException:
        stop_host()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action", choices=["up", "stop", "status", "logs", "check", "restart"]
    )
    parser.add_argument("--mode", choices=["docker", "host"], default=None)
    options = parser.parse_args()
    LOGS.mkdir(parents=True, exist_ok=True)
    state = load_state()
    mode = options.mode or (
        state.get("mode", "docker") if options.action != "up" else "docker"
    )
    try:
        if options.action == "stop":
            stop_host()
        ensure_environment(create=options.action == "up")
        if options.action == "up":
            if mode == "host":
                start_host()
            else:
                stop_host()
                require_free_ports(allow_docker=True)
                run(
                    COMPOSE + ["up", "-d", "--build", "--wait", "--wait-timeout", "240"]
                )
                STATE.write_text(json.dumps({"mode": "docker", "processes": {}}))
                verify(timeout=240)
        elif options.action == "stop":
            stop_host()
            run(COMPOSE + ["stop"])
            print(
                "Stopped owned host processes and Compose services. Persistent volumes retained."
            )
            return 0
        elif options.action == "restart":
            run(
                COMPOSE
                + ["restart"]
                + (
                    ["postgres", "rabbitmq"]
                    if mode == "host"
                    else ["postgres", "rabbitmq", "api", "client"]
                )
            )
            run(
                COMPOSE
                + ["up", "-d", "--wait", "--wait-timeout", "240"]
                + (["postgres", "rabbitmq"] if mode == "host" else [])
            )
            verify(timeout=240)
        elif options.action == "logs":
            run(COMPOSE + ["logs", "--tail", "60", "--no-color"])
            if mode == "host":
                for name in ("api", "ui", "migrations"):
                    path = LOGS / (name + ".log")
                    if path.exists():
                        print(
                            f"{name}: {path}\n"
                            + path.read_text(encoding="utf-8", errors="replace")[-4000:]
                        )
            return 0
        elif options.action == "status":
            run(COMPOSE + ["ps", "-a"])
            print(
                f"Mode: {state.get('mode')}; host processes: {state.get('processes', {})}"
            )
            print(f"Listening: 4200={port_open(4200)}, 5240={port_open(5240)}")
            return 0
        else:
            verify(timeout=15)
        print(
            f"READY ({mode})\nFrontend: {UI}/factory\nAPI: {API}/api/v1/system-health\nAPI + PostgreSQL + RabbitMQ: {API}/health/ready\nRabbitMQ management: http://127.0.0.1:15682\nLogs/checks: {LOGS}\nCodex runner is independent and autonomous execution remains disabled."
        )
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"Environment failed: {error}", file=sys.stderr)
        print(f"Run: python {ROOT / 'scripts/environment.py'} logs", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
