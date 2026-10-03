"""Verify and hash the exact external publication before mathematical work."""
from __future__ import annotations

import sys

from common import ROOT, sha256


def main() -> int:
    publication = ROOT / "yayınlanan.pdf"
    if not publication.is_file():
        print("G0A-T02 input absent: place the exact published yayınlanan.pdf in the repository root.", file=sys.stderr)
        return 1
    with publication.open("rb") as stream:
        if not stream.read(1024).lstrip().startswith(b"%PDF-"):
            print("The supplied input is not a PDF.", file=sys.stderr)
            return 1
    print(f"publication: yayınlanan.pdf\nsha256: {sha256(publication)}")
    print("Record this hash in the G0A-T02 input/config; verify bibliographic identity before deriving equations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
