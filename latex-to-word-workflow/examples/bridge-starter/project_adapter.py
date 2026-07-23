from __future__ import annotations

import argparse
import json
from pathlib import Path

from docx_bridge import DocxPackage, apply_style_remaps, load_config


def adapt(input_path: Path, output_path: Path, config_path: Path) -> dict:
    config = load_config(config_path)
    package = DocxPackage(input_path)
    root = package.xml()

    changed_styles = apply_style_remaps(root, config.get("style_remap", {}))

    # Add only target-specific transformations here. Reuse docx_bridge helpers
    # for fields, bookmarks, runs, styles, and package writes.

    package.set_xml(root)
    package.write(output_path)
    return {"output": str(output_path), "style_remaps": changed_styles}


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply project-specific Word bridge rules.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("bridge_config.json"))
    args = parser.parse_args()
    print(json.dumps(adapt(args.input, args.output, args.config), indent=2))


if __name__ == "__main__":
    main()
