"""Collect sanitized runtime evidence. Never serialize container environment values."""

from datetime import datetime, timezone
import json
import subprocess

from environment import COMPOSE, LOGS, verify


def main() -> None:
    checks = verify()
    services = []
    for line in subprocess.check_output(
        COMPOSE + ["ps", "-a", "--format", "json"], text=True
    ).splitlines():
        record = json.loads(line)
        services.append(
            {
                key: record.get(key)
                for key in (
                    "Service",
                    "State",
                    "Health",
                    "ExitCode",
                    "Publishers",
                    "Image",
                )
            }
        )
    isolation = []
    for service in ("api", "client"):
        cid = subprocess.check_output(
            COMPOSE + ["ps", "-q", service], text=True
        ).strip()
        container = json.loads(
            subprocess.check_output(["docker", "inspect", cid], text=True)
        )[0]
        keys = [entry.split("=", 1)[0] for entry in container["Config"]["Env"]]
        if any(key.startswith(("CODEX", "OPENAI", "RUNNER")) for key in keys):
            raise RuntimeError(
                "Forbidden provider or runner credential configuration in " + service
            )
        mounts = container["Mounts"]
        if any(
            ".codex" in mount["Source"].lower()
            or "docker.sock" in mount["Source"].lower()
            for mount in mounts
        ):
            raise RuntimeError("Forbidden credential/socket mount in " + service)
        if container["HostConfig"]["Privileged"]:
            raise RuntimeError("Privileged container is not allowed")
        command = [
            "sh",
            "-c",
            "! command -v codex >/dev/null 2>&1 && test ! -d /home/app/.codex && test ! -d /home/node/.codex",
        ]
        subprocess.run(COMPOSE + ["exec", "-T", service] + command, check=True)
        uid = subprocess.check_output(
            COMPOSE + ["exec", "-T", service, "id", "-u"], text=True
        ).strip()
        if uid == "0":
            raise RuntimeError("Web service unexpectedly running as root")
        isolation.append(
            {
                "service": service,
                "uid": uid,
                "codexInstalled": False,
                "providerOrRunnerCredentialsPassed": False,
                "privileged": False,
                "credentialOrSocketMounts": False,
            }
        )
    report = {
        "timestampUtc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "services": services,
        "containerBoundaries": isolation,
    }
    (LOGS / "snapshot.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        "PASS: four web/infrastructure services inspected; no Codex, runner credentials, privileged mode or credential/socket mounts"
    )


if __name__ == "__main__":
    main()
