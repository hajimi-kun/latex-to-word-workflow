from __future__ import annotations

import argparse
import shutil
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
STARTER = SKILL_ROOT / "examples" / "bridge-starter"
ENGINE = SKILL_ROOT / "scripts" / "docx_bridge.py"


def initialize(destination: Path, force: bool = False) -> list[Path]:
    destination.mkdir(parents=True, exist_ok=True)
    sources = [*sorted(source for source in STARTER.iterdir() if source.is_file()), ENGINE]
    created: list[Path] = []
    for source in sources:
        target = destination / source.name
        if target.exists() and not force:
            raise FileExistsError(f"refusing to overwrite existing bridge file: {target}")
        shutil.copy2(source, target)
        created.append(target)
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Copy the canonical DOCX bridge starter into a project build directory.")
    parser.add_argument("destination", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    for path in initialize(args.destination, args.force):
        print(path)


if __name__ == "__main__":
    main()
