#!/usr/bin/env python3
"""
make_images_json.py
Scan a directory recursively for image files and write images.json.

Usage:
    python make_images_json.py              # scans current directory
    python make_images_json.py /path/to/dir
Options:
    --extensions .jpg,.jpeg,.png,.gif,.webp,.avif,.bmp
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Try to import Pillow for image dimensions; if not available we'll skip width/height.
try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif', '.bmp', '.tiff', '.svg'}

def scan_images(root: Path, exts=set()):
    items = []
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.suffix.lower() in exts:
                rel = p.relative_to(root).as_posix()
                try:
                    stat = p.stat()
                    meta = {
                        "path": rel,
                        "name": p.name,
                        "size_bytes": stat.st_size,
                        "modified": datetime.utcfromtimestamp(stat.st_mtime).isoformat() + "Z"
                    }
                    if PIL_AVAILABLE and p.suffix.lower() != '.svg':
                        try:
                            with Image.open(p) as im:
                                meta["width"], meta["height"] = im.size
                                meta["mode"] = im.mode
                        except Exception:
                            # ignore dimension extraction failures
                            pass
                    items.append(meta)
                except Exception as e:
                    print(f"Warning: couldn't stat {p}: {e}", file=sys.stderr)
    return items

def main():
    parser = argparse.ArgumentParser(description="Scan dir for images and create images.json")
    parser.add_argument("root", nargs="?", default=".", help="Root directory to scan")
    parser.add_argument("--extensions", default=",".join(sorted(IMAGE_EXTS)),
                        help="Comma-separated list of extensions (with dot).")
    parser.add_argument("--out", default="images.json", help="Output json filename")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    exts = {e.strip().lower() for e in args.extensions.split(",") if e.strip()}
    print(f"Scanning {root} for extensions: {', '.join(sorted(exts))}")

    images = scan_images(root, exts)
    images.sort(key=lambda x: x.get("name","").lower())

    out_path = root / args.out
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(images, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(images)} entries to {out_path}")

if __name__ == "__main__":
    main()
