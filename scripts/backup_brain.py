"""Consistent Brain backup and isolated restore test. No live database restore."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import uuid
import zipfile

from environment import COMPOSE, ROOT, verify, load_state
from dev_config import local_values


def run(arguments: list[str], **kwargs: object) -> subprocess.CompletedProcess:
    return subprocess.run(arguments, check=True, **kwargs)


def create() -> Path:
    if load_state().get("mode") != "docker":
        raise RuntimeError(
            "Consistent backup requires Docker mode. Run environment.py up before backup; no host writer may remain active."
        )
    folder = (
        ROOT
        / "artifacts/local/brain-backups"
        / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    )
    folder.mkdir(parents=True, exist_ok=False)
    # The API is the only writer. Stopping it freezes promotion refs and metadata.
    run(COMPOSE + ["stop", "api"])
    try:
        with (folder / "postgres.dump").open("wb") as stream:
            run(
                COMPOSE
                + [
                    "exec",
                    "-T",
                    "postgres",
                    "pg_dump",
                    "-U",
                    "factory",
                    "-d",
                    "codefactory",
                    "-Fc",
                ],
                stdout=stream,
            )
        run(
            [
                "git",
                "-C",
                str(ROOT),
                "bundle",
                "create",
                str(folder / "knowledge.bundle"),
                "--all",
            ]
        )
        with zipfile.ZipFile(
            folder / "state.zip", "w", zipfile.ZIP_DEFLATED
        ) as archive:
            for path in (ROOT / "artifacts/local/brain/keys").glob("*.xml"):
                archive.write(path, "keys/" + path.name)
        refs = subprocess.check_output(
            [
                "git",
                "-C",
                str(ROOT),
                "for-each-ref",
                "--format=%(objectname) %(refname)",
                "refs/brain/official/",
            ],
            text=True,
        ).splitlines()
        manifest = {
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "refs": refs,
            "sha256": {
                name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
                for name in ["postgres.dump", "knowledge.bundle", "state.zip"]
            },
            "sensitiveBackup": True,
            "officialSource": "Git objects plus PostgreSQL verified revision pointers",
        }
        (folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    finally:
        run(
            COMPOSE
            + ["up", "-d", "--no-deps", "--wait", "--wait-timeout", "180", "api"]
        )
        verify()
    print("Backup created (private, ignored):", folder)
    return folder


def restore_test(folder: Path) -> None:
    import psycopg
    from psycopg import sql

    manifest = json.loads((folder / "manifest.json").read_text())
    for name, digest in manifest["sha256"].items():
        if (
            name not in {"postgres.dump", "knowledge.bundle", "state.zip"}
            or hashlib.sha256((folder / name).read_bytes()).hexdigest() != digest
        ):
            raise RuntimeError("Backup integrity check failed")
    run(["git", "-C", str(ROOT), "bundle", "verify", str(folder / "knowledge.bundle")])
    values = local_values()
    database = "brain_restore_test_" + uuid.uuid4().hex
    if not re.fullmatch(r"brain_restore_test_[a-f0-9]{32}", database):
        raise RuntimeError("Restore test target is not isolated")
    connection = psycopg.connect(
        host="127.0.0.1",
        port=55432,
        dbname="postgres",
        user="factory",
        password=values["POSTGRES_PASSWORD"],
        autocommit=True,
    )
    try:
        connection.execute(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database))
        )
        with (folder / "postgres.dump").open("rb") as stream:
            run(
                COMPOSE
                + [
                    "exec",
                    "-T",
                    "postgres",
                    "pg_restore",
                    "-U",
                    "factory",
                    "--exit-on-error",
                    "--no-owner",
                    "-d",
                    database,
                ],
                stdin=stream,
            )
        with psycopg.connect(
            host="127.0.0.1",
            port=55432,
            dbname=database,
            user="factory",
            password=values["POSTGRES_PASSWORD"],
        ) as restored:
            revisions = restored.execute(
                'SELECT r."Commit",r."Sha256",d."Path" FROM "KnowledgeRevisions" r JOIN "BrainDocuments" d ON d."Id"=r."DocumentId"'
            ).fetchall()
            snapshots = restored.execute(
                'SELECT "PackageHash","PackageJson" FROM "ContextSnapshots"'
            ).fetchall()
            if not revisions:
                raise RuntimeError("Backup did not restore knowledge revisions")
            for commit, digest, path in revisions:
                if not re.fullmatch(r"[a-f0-9]{40}", commit) or not re.fullmatch(
                    r"[a-z0-9][a-z0-9/_-]*\.md", path
                ):
                    raise RuntimeError("Invalid restored source reference")
                body = subprocess.check_output(
                    ["git", "-C", str(ROOT), "show", commit + ":" + path]
                )
                if hashlib.sha256(body).hexdigest() != digest:
                    raise RuntimeError("Restored Git/DB hash mismatch")
            for digest, package in snapshots:
                if hashlib.sha256(package.encode()).hexdigest() != digest:
                    raise RuntimeError("Restored snapshot hash mismatch")
        # Import a backed-up ref into a unique test namespace in the existing repository.
        target = "refs/brain/restore-tests/" + uuid.uuid4().hex
        source = manifest["refs"][0].split(" ", 1)[1]
        run(
            [
                "git",
                "-C",
                str(ROOT),
                "fetch",
                "--no-write-fetch-head",
                str(folder / "knowledge.bundle"),
                source + ":" + target,
            ]
        )
        try:
            expected = manifest["refs"][0].split(" ", 1)[0]
            actual = subprocess.check_output(
                ["git", "-C", str(ROOT), "rev-parse", target], text=True
            ).strip()
            if actual != expected:
                raise RuntimeError("Recovered Git reference mismatch")
        finally:
            run(["git", "-C", str(ROOT), "update-ref", "-d", target])
        evidence = {
            "backup": folder.name,
            "restoredDatabase": "isolated test database removed after verification",
            "revisionsVerified": len(revisions),
            "snapshotsVerified": len(snapshots),
            "gitBundleVerified": True,
            "snapshotHashesVerified": True,
            "liveDataOverwritten": False,
        }
        (ROOT / "artifacts/local/environment/brain-restore.json").write_text(
            json.dumps(evidence, indent=2) + "\n"
        )
        print(
            "PASS: isolated PostgreSQL restore, Git bundle/ref recovery and snapshot hashes",
            len(revisions),
            len(snapshots),
        )
    finally:
        connection.execute(
            sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(
                sql.Identifier(database)
            )
        )
        connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-restore", action="store_true")
    options = parser.parse_args()
    folder = create()
    if options.verify_restore:
        restore_test(folder)
