#!/usr/bin/env python3
"""Expand executed block IDs into the instruction lines from bb_metadata.txt."""
import argparse
from pathlib import Path
import re


def read_metadata(path: Path) -> dict[int, str]:
    blocks: dict[int, list[str]] = {}
    current_block = None
    with path.open(encoding="utf-8") as metadata:
        for line_number, line in enumerate(metadata, start=1):
            header = re.fullmatch(r"BB([0-9]+):", line.strip())
            if header:
                current_block = int(header.group(1))
                if current_block in blocks:
                    raise ValueError(
                        f"{path}:{line_number}: duplicate BB{current_block}"
                    )
                blocks[current_block] = []
            elif line.strip():
                if current_block is None:
                    raise ValueError(
                        f"{path}:{line_number}: expected a BB<number>: header"
                    )
                blocks[current_block].append(line.rstrip("\n") + "\n")
    return {block_id: "".join(lines) for block_id, lines in blocks.items()}


def expand_trace(trace_path: Path, metadata_path: Path, output_path: Path) -> None:
    if output_path.resolve() in (trace_path.resolve(), metadata_path.resolve()):
        raise ValueError("output path must differ from both input paths")

    blocks = read_metadata(metadata_path)
    with trace_path.open(encoding="utf-8") as trace, output_path.open(
        "w", encoding="utf-8"
    ) as output:
        for line_number, line in enumerate(trace, start=1):
            entry = line.strip()
            if not entry:
                continue
            if not re.fullmatch(r"[0-9]+", entry):
                raise ValueError(
                    f"{trace_path}:{line_number}: expected a numeric block ID"
                )
            block_id = int(entry)
            if block_id not in blocks:
                raise ValueError(
                    f"{trace_path}:{line_number}: BB{block_id} is missing from metadata"
                )
            output.write(blocks[block_id])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-t", "--trace", type=Path, required=True,
                        help="trace produced by the launched app")
    parser.add_argument("-m", "--bb-metadata", type=Path, required=True,
                        help="metadata produced by TracingPass")
    parser.add_argument(
        "-o", "--output", type=Path, required=True, help="output file",
    )
    args = parser.parse_args()
    try:
        expand_trace(args.trace, args.bb_metadata, args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{parser.prog}: {error}\n")


if __name__ == "__main__":
    main()
