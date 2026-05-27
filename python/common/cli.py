"""Reusable argparse patterns for SRE CLI tools."""

from __future__ import annotations

import argparse
from typing import Sequence


def build_parser(description: str) -> argparse.ArgumentParser:
    """Standard CLI parser with --verbose flag."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug output")
    return parser


def parse_args(description: str, argv: Sequence[str] | None = None) -> argparse.Namespace:
    return build_parser(description).parse_args(argv)
