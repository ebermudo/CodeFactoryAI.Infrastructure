"""Foreground hot-reload launcher. For persistent all-services startup use environment.py."""

import argparse
import subprocess
import sys

from dev_config import application_command


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Foreground development server. Keep this terminal open; Ctrl+C stops it."
    )
    parser.add_argument("service", choices=["ui", "api", "context", "runner"])
    parser.add_argument(
        "--no-watch", action="store_true", help="Disable dotnet watch for API"
    )
    options = parser.parse_args()
    try:
        command, cwd, env = application_command(
            options.service, watch=not options.no_watch
        )
        print(f"Starting {options.service} in {cwd}", flush=True)
        print(
            "Foreground server: keep this terminal open. For detached startup: python scripts/environment.py up",
            flush=True,
        )
        child = subprocess.Popen(command, cwd=cwd, env=env)
        try:
            return child.wait()
        except KeyboardInterrupt:
            child.terminate()
            child.wait(timeout=15)
            return 130
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"Development startup failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
