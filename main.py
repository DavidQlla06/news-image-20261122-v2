#!/usr/bin/env python3
"""Entrypoint: copy the committed entry.png to the output directory.

Runs with the Python standard library only and no network, as the
make.fun sandbox requires. The image itself is drawn ahead of time by
generate.py from stories.json; this program just places the bytes.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)


if __name__ == "__main__":
    main()
