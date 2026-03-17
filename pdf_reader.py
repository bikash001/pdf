#!/usr/bin/env python3
"""PDF reader utility for encrypted and unencrypted PDF files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pypdf import PdfReader


class PDFReaderError(Exception):
    """Raised when reading or processing a PDF fails."""


def _import_pypdf() -> tuple[Any, Any]:
    try:
        from pypdf import PdfReader, PdfWriter
    except ModuleNotFoundError as exc:
        raise PDFReaderError(
            "Missing dependency 'pypdf'. Install it with: pip install -r requirements.txt"
        ) from exc
    return PdfReader, PdfWriter


def load_reader(path: Path, password: str | None = None) -> "PdfReader":
    """Load a PDF file and decrypt it if needed."""
    PdfReader, _ = _import_pypdf()
    try:
        reader = PdfReader(str(path))
    except Exception as exc:  # pragma: no cover - library-specific errors
        raise PDFReaderError(f"Could not open '{path}': {exc}") from exc

    if reader.is_encrypted:
        if password is None:
            raise PDFReaderError("PDF is password-protected. Provide --password.")
        result = reader.decrypt(password)
        if result == 0:
            raise PDFReaderError("Incorrect password for encrypted PDF.")

    return reader


def print_info(reader: "PdfReader", path: Path) -> None:
    """Print basic document details."""
    meta = reader.metadata or {}
    title = meta.get("/Title", "Unknown")
    author = meta.get("/Author", "Unknown")
    subject = meta.get("/Subject", "Unknown")
    print(f"File: {path}")
    print(f"Pages: {len(reader.pages)}")
    print(f"Title: {title}")
    print(f"Author: {author}")
    print(f"Subject: {subject}")


def extract_text(reader: "PdfReader") -> str:
    """Extract text from all pages."""
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        parts.append(text)
    return "\n".join(parts).strip()


def save_unlocked_copy(reader: "PdfReader", output_path: Path) -> None:
    """Save a copy of the PDF without password protection."""
    _, PdfWriter = _import_pypdf()
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    # Not setting encryption keeps output unencrypted.
    try:
        with output_path.open("wb") as fh:
            writer.write(fh)
    except Exception as exc:  # pragma: no cover - filesystem-related
        raise PDFReaderError(f"Could not write '{output_path}': {exc}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read encrypted PDFs and save password-free copies."
    )
    parser.add_argument("input", help="Path to input PDF")

    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_password_arg(cmd_parser: argparse.ArgumentParser) -> None:
        cmd_parser.add_argument(
            "--password",
            default=None,
            help="Password for encrypted PDF (omit for unencrypted files)",
        )

    info_parser = subparsers.add_parser("info", help="Print PDF metadata and page count")
    add_password_arg(info_parser)

    text_parser = subparsers.add_parser("extract-text", help="Extract text content")
    add_password_arg(text_parser)
    text_parser.add_argument(
        "--out",
        default=None,
        help="Optional text output file; prints to terminal if omitted",
    )

    unlock_parser = subparsers.add_parser(
        "unlock", help="Save password-free copy of PDF"
    )
    add_password_arg(unlock_parser)
    unlock_parser.add_argument(
        "--out",
        required=True,
        help="Output path for unlocked PDF copy",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        reader = load_reader(input_path, args.password)
        if args.command == "info":
            print_info(reader, input_path)
        elif args.command == "extract-text":
            content = extract_text(reader)
            if args.out:
                out_path = Path(args.out).expanduser().resolve()
                out_path.write_text(content, encoding="utf-8")
                print(f"Text extracted to: {out_path}")
            else:
                print(content)
        elif args.command == "unlock":
            out_path = Path(args.out).expanduser().resolve()
            save_unlocked_copy(reader, out_path)
            print(f"Unlocked PDF saved to: {out_path}")
        else:  # pragma: no cover - parser enforces valid command
            parser.error("Unknown command")
    except PDFReaderError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
