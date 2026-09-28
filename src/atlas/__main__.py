"""CLI entry point for ATLAS: py -3.11 -m atlas."""

import argparse
import sys

from atlas import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the ATLAS CLI."""
    parser = argparse.ArgumentParser(
        prog="atlas",
        description="ATLAS — JARVIS-style Voice Assistant for Windows 11",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"atlas {__version__}",
        help="Show ATLAS version and exit.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Main CLI execution handler."""
    parser = build_parser()
    _ = parser.parse_args(argv)
    # Default behavior for now:
    print(f"ATLAS v{__version__} — ready. Use --help for available options.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
