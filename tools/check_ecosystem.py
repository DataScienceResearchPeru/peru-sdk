"""Consume pinned SDK repositories and verify their isolated distributions."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.request import urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OWNER = "DataScienceResearchPeru"


def read_file(repository, revision, path):
    if not re.fullmatch(r"peru-sdk-(models|conformance|go|python)", repository) or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("expected a component repository and a full immutable commit")
    with urlopen(f"https://raw.githubusercontent.com/{OWNER}/{repository}/{revision}/{path}", timeout=30) as response:
        body = response.read(2 * 1024 * 1024 + 1)
    if len(body) > 2 * 1024 * 1024:
        raise ValueError("upstream file exceeds its limit")
    return body


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    output = parser.parse_args().output.resolve()
    if output.exists() and any(output.iterdir()):
        raise SystemExit("verification destination must be empty")
    output.mkdir(parents=True, exist_ok=True)
    lock = json.loads((ROOT / "ecosystem.lock.json").read_text())
    if lock["format_version"] != 1:
        raise SystemExit("unsupported ecosystem lock")
    corpus = lock["conformance"]
    body = read_file(corpus["repository"], corpus["revision"], "cases.json")
    if hashlib.sha256(body).hexdigest() != corpus["sha256"]:
        raise SystemExit("shared corpus integrity mismatch")
    report = {"models": lock["models"], "conformance": corpus, "sdks": {}}
    Path("/var/tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="peru-ecosystem-", dir="/var/tmp") as directory:
        task = Path(directory)
        env = {**os.environ, "TMPDIR": directory, "TEMP": directory, "TMP": directory,
               "PYTHONDONTWRITEBYTECODE": "1", "PIP_DISABLE_PIP_VERSION_CHECK": "1"}

        def run(*command, cwd=task):
            subprocess.run(command, cwd=cwd, env=env, check=True)

        for language, sdk in lock["sdks"].items():
            raw = read_file(sdk["repository"], sdk["revision"], "upstream.lock.json")
            if hashlib.sha256(raw).hexdigest() != sdk["upstream_lock_sha256"]:
                raise SystemExit("SDK upstream lock integrity mismatch")
            upstream = json.loads(raw)
            if upstream["language"] != language or upstream["generator"]["revision"] != lock["models"]["revision"]:
                raise SystemExit("SDK language or model revision mismatch")
            if upstream["generator"]["repository"] != OWNER + "/" + lock["models"]["repository"]:
                raise SystemExit("SDK uses another model repository")
            if upstream["conformance"]["revision"] != corpus["revision"] or upstream["conformance"]["sha256"] != corpus["sha256"]:
                raise SystemExit("SDK uses another conformance corpus")
            source = task / language
            run("git", "init", "--quiet", str(source))
            run("git", "remote", "add", "origin", f"https://github.com/{OWNER}/{sdk['repository']}.git", cwd=source)
            run("git", "fetch", "--quiet", "--depth=1", "origin", sdk["revision"], cwd=source)
            run("git", "checkout", "--quiet", "--detach", "FETCH_HEAD", cwd=source)
            actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
            if actual != sdk["revision"]:
                raise SystemExit("checkout did not resolve the expected commit")
            run(sys.executable, ".ci/check_package.py", "--output", str(output / language), cwd=source)
            report["sdks"][language] = json.loads((output / language / "manifest/release.json").read_text())
            if language == "go":
                consumer = task / "public-go-consumer"
                consumer.mkdir()
                shutil.copyfile(source / "examples/offline/main.go", consumer / "main.go")
                run("go", "mod", "init", "consumer.example/published", cwd=consumer)
                module = "github.com/" + OWNER + "/" + sdk["repository"]
                run("go", "get", module + "@" + sdk["revision"], cwd=consumer)
                run("go", "run", ".", cwd=consumer)
                run("go", "test", module + "/reniec", module + "/sunat", cwd=consumer)
                download = json.loads(subprocess.check_output(["go", "mod", "download", "-json", module], cwd=consumer, env=env, text=True))
                with zipfile.ZipFile(download["Zip"]) as archive:
                    if any("/src/peru_sdk/" in name or "/sdk-python/" in name or name.endswith((".whl", ".jar")) for name in archive.namelist()):
                        raise SystemExit("foreign SDK in published Go module")
    report["shared_cases"] = sum(len(json.loads(body)[key]) for key in ("query_cases", "response_cases", "identity_cases"))
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print("Verified independent SDKs and public Go module. Report:", output / "report.json")


if __name__ == "__main__":
    main()
