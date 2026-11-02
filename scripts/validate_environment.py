"""Real outage/restart probes of this Compose project only. Leave it healthy."""

from datetime import datetime, timezone
import json
import subprocess
import sys
import time

from environment import API, UI, COMPOSE, LOGS, ROOT, http, verify


def main() -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    results = []
    results.append({"stage": "initial", **verify()})
    for service in ("rabbitmq", "postgres"):
        try:
            subprocess.run(COMPOSE + ["stop", service], check=True)
            deadline = time.monotonic() + 30
            while True:
                status, body, _ = http(API + "/health/ready")
                if status == 503:
                    break
                if time.monotonic() >= deadline:
                    raise RuntimeError(f"Readiness did not fail when {service} stopped")
                time.sleep(1)
            status_live, _, _ = http(API + "/health/live")
            if status_live != 200:
                raise RuntimeError(
                    "Liveness must stay available during dependency outage"
                )
            proxy_status, _, _ = http(UI + "/health/ready")
            if proxy_status != 503:
                raise RuntimeError("Angular proxy did not preserve API failure status")
            results.append(
                {
                    "stage": service + "-outage",
                    "apiReadyHttp": 503,
                    "apiLiveHttp": 200,
                    "proxyReadyHttp": 503,
                }
            )
            print(
                f"{service} outage: readiness 503, liveness 200, proxy 503", flush=True
            )
        finally:
            subprocess.run(
                COMPOSE
                + ["up", "-d", "--no-deps", "--wait", "--wait-timeout", "180", service],
                check=True,
            )
        results.append({"stage": service + "-recovered", **verify()})
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/environment.py"),
            "restart",
            "--mode",
            "docker",
        ],
        check=True,
    )
    results.append({"stage": "all-containers-restarted", **verify()})
    (LOGS / "recovery.json").write_text(
        json.dumps(
            {
                "timestampUtc": datetime.now(timezone.utc).isoformat(),
                "results": results,
            },
            indent=2,
        )
        + "\n"
    )
    print(
        "PASS: real dependency outages and complete container restart recovered",
        flush=True,
    )


if __name__ == "__main__":
    main()
