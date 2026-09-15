"""Create a deployable dist/ folder containing only static pages and assets."""

import json
import shutil
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist"


def main() -> None:
    pages = json.loads((ROOT / "content/navigation.json").read_text())["pages"]
    OUTPUT.mkdir(exist_ok=True)
    for page in pages:
        target = OUTPUT / page["route"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / page["route"], target)
    shutil.copytree(ROOT / "assets", OUTPUT / "assets", dirs_exist_ok=True)

    redirects = []
    url_map = json.loads((ROOT / "content/url-map.json").read_text())
    for source, target in url_map.items():
        original_path = urlsplit(source).path
        if original_path != "/":
            redirects.append(f"{original_path} /{target} 301")
    (OUTPUT / "_redirects").write_text("\n".join(redirects) + "\n")
    print(f"Packaged {len(pages)} pages in {OUTPUT}")


if __name__ == "__main__":
    main()
