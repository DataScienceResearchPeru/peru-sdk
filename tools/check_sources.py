"""Report changed official documents separately from unavailable sources; never update rules."""
import hashlib
import json
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    manifest = json.loads((ROOT / "contracts/sources.lock.json").read_text(encoding="utf-8"))
    changed = unavailable = False
    for source in manifest["sources"]:
        try:
            with urlopen(source["url"], timeout=30) as response:
                body = response.read(16 * 1024 * 1024 + 1)
            if len(body) > 16 * 1024 * 1024 or not body.startswith(b"%PDF-"):
                raise ValueError("response is not a bounded PDF")
            digest = hashlib.sha256(body).hexdigest()
            if digest != source["sha256"]:
                changed = True
                print(f"CHANGED {source['id']}: {source['sha256']} -> {digest}; review required")
            else:
                print(f"UNCHANGED {source['id']}")
        except (URLError, OSError, ValueError) as error:
            unavailable = True
            print(f"UNAVAILABLE {source['id']}: {type(error).__name__}; compatibility is not evaluated")
    return 2 if unavailable else 1 if changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
