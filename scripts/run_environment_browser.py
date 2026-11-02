"""Real Chromium connectivity test using the portable local Node installation."""
import json
import subprocess

from dev_config import ROOT, WORKSPACE, host_configuration

def main() -> int:
    env, node = host_configuration()
    client = WORKSPACE / "CodeFactoryAI.ClientAngular"
    output = ROOT / "artifacts/local/environment"
    output.mkdir(parents=True, exist_ok=True)
    with (output / "browser.json").open("w", encoding="utf-8") as stdout, (output / "browser.log").open("w", encoding="utf-8") as stderr:
        result = subprocess.run([str(node / "node.exe"), str(client / "node_modules/@playwright/test/cli.js"), "test", "--config", "playwright.environment.config.ts", "--reporter=json"], cwd=client, env=env, stdout=stdout, stderr=stderr, check=False, timeout=120)
    if result.returncode:
        print(f"FAIL: browser test; inspect {output / 'browser.json'} and browser.log")
        return result.returncode
    stats = json.loads((output / "browser.json").read_text(encoding="utf-8"))["stats"]
    print(f"PASS: browser integration ({stats['expected']} passed, {stats['unexpected']} failed, {stats['skipped']} skipped)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
