"""Portable toolchain installer; no global install, PATH or registry changes."""
from pathlib import Path
import hashlib
import json
import urllib.request
import zipfile

root = Path(__file__).resolve().parents[1]
versions = json.loads((root / "toolchain.json").read_text())
tools = root / ".tools"
tools.mkdir(exist_ok=True)

def install(url: str, checksum: str, algorithm: str, destination: Path, executable: Path) -> None:
    if executable.exists():
        print(f"Already present: {executable.name}")
        return
    data = urllib.request.urlopen(url, timeout=120).read()
    if hashlib.new(algorithm, data).hexdigest().lower() != checksum.lower():
        raise RuntimeError("Official archive checksum mismatch")
    archive = tools / (algorithm + "-download.zip")
    archive.write_bytes(data)
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as contents:
        for member in contents.namelist():
            target = (destination / member).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise RuntimeError("Unsafe archive path")
        contents.extractall(destination)
    print(f"Installed portable tool: {executable.name}")

sdk = versions["dotnet"]
node = versions["node"]
install(f"https://builds.dotnet.microsoft.com/dotnet/Sdk/{sdk}/dotnet-sdk-{sdk}-win-x64.zip", versions["dotnetSha512"], "sha512", tools / "dotnet", tools / "dotnet/dotnet.exe")
install(f"https://nodejs.org/dist/{node}/node-{node}-win-x64.zip", versions["nodeSha256"], "sha256", tools / "node-download", tools / f"node-download/node-{node}-win-x64/node.exe")
