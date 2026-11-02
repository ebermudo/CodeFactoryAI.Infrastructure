"""Explicit real hot-reload probes; always restore source bytes."""

import json
import time

from environment import API, UI, LOGS, WORKSPACE, http, load_state, verify


def wait_for(predicate, description: str) -> None:
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        try:
            if predicate():
                return
        except (OSError, ValueError):
            pass
        time.sleep(1)
    raise RuntimeError(f"Hot reload timeout: {description}")


def main() -> None:
    if load_state().get("mode") != "host":
        raise RuntimeError("Use environment.py up --mode host before this probe")
    verify()
    index = WORKSPACE / "CodeFactoryAI.ClientAngular/src/index.html"
    controller = (
        WORKSPACE
        / "CodeFactoryAI.API/src/CodeFactoryAI.Api/Controllers/SystemHealthController.cs"
    )
    index_before = index.read_bytes()
    controller_before = controller.read_bytes()
    marker = b"<!-- codefactory-live-reload-probe -->"
    original = b'status = "foundation"'
    replacement = b'status = "foundation-reload-probe"'
    if controller_before.count(original) != 1:
        raise RuntimeError("Unexpected controller contents; no probe applied")
    try:
        index.write_bytes(index_before + b"\n" + marker + b"\n")
        wait_for(lambda: marker in http(UI + "/factory")[1], "Angular index change")
        controller.write_bytes(controller_before.replace(original, replacement, 1))
        wait_for(
            lambda: json.loads(http(API + "/api/v1/system-health")[1])["status"]
            == "foundation-reload-probe",
            ".NET watch code change",
        )
    finally:
        index.write_bytes(index_before)
        controller.write_bytes(controller_before)
    wait_for(lambda: marker not in http(UI + "/factory")[1], "Angular restored")
    wait_for(
        lambda: json.loads(http(API + "/api/v1/system-health")[1])["status"]
        == "foundation",
        ".NET restored",
    )
    assert index.read_bytes() == index_before
    assert controller.read_bytes() == controller_before
    (LOGS / "hot-reload.json").write_text(
        json.dumps(
            {
                "mode": "host",
                "angularHotReload": True,
                "dotnetHotReload": True,
                "sourceBytesRestored": True,
            },
            indent=2,
        )
        + "\n"
    )
    print("PASS: Angular and .NET host hot reload observed over HTTP; sources restored")


if __name__ == "__main__":
    main()
