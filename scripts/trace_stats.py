"""Count frequent metadata-line patterns directly from an app's block trace."""

import argparse
from collections import Counter
import csv
from pathlib import Path
import re


MAX_LENGTH = 5
# Bound additional memory even when a trace has many distinct boundary contexts.
BOUNDARY_BATCH_SIZE = 50_000
Pattern = tuple[str, ...]


def read_metadata(path: Path) -> dict[int, Pattern]:
    blocks: dict[int, list[str]] = {}
    current_block = None
    with path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            entry = line.strip()
            if not entry:
                continue
            header = re.fullmatch(r"BB([0-9]+):", entry)
            if header:
                current_block = int(header.group(1))
                if current_block in blocks:
                    raise ValueError(f"{path}:{line_number}: duplicate BB{current_block}")
                blocks[current_block] = []
            elif current_block is None:
                raise ValueError(f"{path}:{line_number}: expected a BB<number>: header")
            else:
                blocks[current_block].append(entry)
    return {block_id: tuple(lines) for block_id, lines in blocks.items()}


def count_patterns(
    trace_path: Path, blocks: dict[int, Pattern], max_length: int = MAX_LENGTH + 1
) -> dict[int, Counter[Pattern]]:
    """Weight internal windows and repeated boundary contexts by their visits.

    Occurrences may overlap. Empty blocks contribute no lines and do not break
    patterns. The extra length permits filtering extensions of length-5 patterns.
    """
    counts: dict[int, Counter[Pattern]] = {
        length: Counter() for length in range(1, max_length + 1)
    }
    visits: dict[int, int] = {}
    boundaries: dict[tuple[Pattern, Pattern], int] = {}
    tail: Pattern = ()
    tail_length = max_length - 1
    edges = {
        block_id: (block[:tail_length], block[-tail_length:] if tail_length else (), len(block))
        for block_id, block in blocks.items()
    }

    def flush_boundaries() -> None:
        for (before, after), frequency in boundaries.items():
            # Each crossing window is a suffix of earlier executed blocks
            # followed by a prefix of the current block. Windows spanning
            # several short blocks are included in 'before'.
            for length in range(2, max_length + 1):
                first_left = max(1, length - len(after))
                last_left = min(length - 1, len(before))
                for left_size in range(first_left, last_left + 1):
                    pattern = before[-left_size:] + after[:length - left_size]
                    counts[length][pattern] += frequency
        boundaries.clear()

    with trace_path.open(encoding="utf-8") as trace:
        for line_number, line in enumerate(trace, 1):
            entry = line.strip()
            if not entry:
                continue
            if not (entry.isascii() and entry.isdecimal()):
                raise ValueError(f"{trace_path}:{line_number}: expected a numeric block ID")
            block_id = int(entry)
            try:
                head, suffix, block_size = edges[block_id]
            except KeyError:
                raise ValueError(
                    f"{trace_path}:{line_number}: BB{block_id} is missing from metadata"
                )
            visits[block_id] = visits.get(block_id, 0) + 1
            if not block_size or not tail_length:
                continue

            if tail:
                context = (tail, head)
                boundaries[context] = boundaries.get(context, 0) + 1
                if len(boundaries) >= BOUNDARY_BATCH_SIZE:
                    flush_boundaries()
            tail = suffix if block_size >= tail_length else (tail + suffix)[-tail_length:]

    flush_boundaries()

    # Process each executed block's internal windows just once, even if the
    # trace visits that block millions of times.
    for block_id, frequency in visits.items():
        block = blocks[block_id]
        for length in range(1, min(max_length, len(block)) + 1):
            for start in range(len(block) - length + 1):
                counts[length][block[start:start + length]] += frequency
    return counts


def filter_patterns(
    counts: dict[int, Counter[Pattern]], max_length: int = MAX_LENGTH
) -> dict[int, Counter[Pattern]]:
    """Keep patterns with no left or right extension having the same count.

    Checking one-line extensions suffices: any longer containing pattern with
    the same count has an immediate extension with that count too. Filter using
    the original counts, so removal of an extension cannot restore a subpattern.
    """
    filtered = {}
    for length in range(1, max_length + 1):
        redundant = set()
        for longer, frequency in counts[length + 1].items():
            for shorter in (longer[:-1], longer[1:]):
                if counts[length][shorter] == frequency:
                    redundant.add(shorter)
        filtered[length] = Counter({
            pattern: frequency for pattern, frequency in counts[length].items()
            if pattern not in redundant
        })
    return filtered


def create_chart(length: int, ranked: list[tuple[Pattern, int]], k: int):
    """Build a Matplotlib column chart with exact occurrence counts as heights."""
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    from matplotlib.ticker import MaxNLocator

    top = ranked[:k]
    longest_line = max((len(line) for pattern, _ in top for line in pattern), default=0)
    slot_width = max(1.5, longest_line * 0.08 + 0.3)
    figure = Figure(figsize=(max(9, len(top) * slot_width), 5.5 + length * 0.2),
                    layout="constrained")
    # Use a file-rendering canvas so no GUI or display server is required.
    FigureCanvasAgg(figure)
    axes = figure.subplots()
    axes.set_title(f"Top {k} patterns of length {length}\n"
                   f"{len(top)} shown of {len(ranked)} retained patterns", pad=14)
    axes.set_xlabel("Pattern (metadata lines in execution order, top to bottom)", labelpad=12)
    axes.set_ylabel("Occurrences")
    axes.yaxis.set_major_locator(MaxNLocator(nbins=6, integer=True))
    axes.ticklabel_format(axis="y", style="plain", useOffset=False)
    axes.set_axisbelow(True)
    axes.grid(axis="y", color="#dce2eb")
    axes.spines["top"].set_visible(False)
    axes.spines["right"].set_visible(False)
    if top:
        positions = list(range(len(top)))
        frequencies = [frequency for _, frequency in top]
        bars = axes.bar(positions, frequencies, width=0.65, color="#2563eb")
        axes.set_xticks(positions, ["\n".join(pattern) for pattern, _ in top], fontsize=9)
        axes.bar_label(bars, labels=[f"{frequency:,}" for frequency in frequencies],
                       padding=4, fontsize=9)
        axes.set_ylim(0, max(frequencies) * 1.15)
    else:
        axes.set_xticks([])
        axes.set_ylim(0, 1)
        axes.text(0.5, 0.5, "No retained patterns of this length", transform=axes.transAxes,
                  ha="center", va="center", fontsize=14)
    return figure


def write_chart(path: Path, length: int, ranked: list[tuple[Pattern, int]], k: int) -> None:
    figure = create_chart(length, ranked, k)
    figure.savefig(path, dpi=150, bbox_inches="tight")


def positive_integer(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-t", "--trace", type=Path, required=True,
                        help="numeric block IDs from the launched app")
    parser.add_argument("-m", "--bb-metadata", type=Path, required=True,
                        help="metadata produced by TracingPass")
    parser.add_argument("-k", "--top-k", type=positive_integer, default=10,
                        help="maximum patterns per chart (default: 10)")
    parser.add_argument("-o", "--output-dir", type=Path, required=True,
                        help="output directory containing csv/ and images/ subdirectories")
    args = parser.parse_args()
    output_dir = args.output_dir
    csv_dir = output_dir / "csv"
    image_dir = output_dir / "images"
    try:
        inputs = {args.trace.resolve(), args.bb_metadata.resolve()}
        for length in range(1, MAX_LENGTH + 1):
            for path in (csv_dir / f"patterns_{length}.csv",
                         image_dir / f"patterns_{length}.png"):
                if path.resolve() in inputs:
                    raise ValueError("output files must differ from the input paths")
        blocks = read_metadata(args.bb_metadata)
        counts = filter_patterns(count_patterns(args.trace, blocks))
        csv_dir.mkdir(parents=True, exist_ok=True)
        image_dir.mkdir(parents=True, exist_ok=True)
        for length in range(1, MAX_LENGTH + 1):
            ranked = sorted(counts[length].items(), key=lambda item: (-item[1], item[0]))
            with (csv_dir / f"patterns_{length}.csv").open(
                "w", encoding="utf-8", newline=""
            ) as output:
                writer = csv.writer(output)
                writer.writerow(["pattern", "occurrences"])
                writer.writerows((" | ".join(pattern), frequency) for pattern, frequency in ranked)
            write_chart(image_dir / f"patterns_{length}.png", length, ranked, args.top_k)
    except ModuleNotFoundError as error:
        if error.name != "matplotlib":
            raise
        parser.exit(1, f"{parser.prog}: Matplotlib is required. Enter the Nix shell with:\n"
                    "  nix develop\n")
    except (OSError, ValueError) as error:
        parser.exit(1, f"{parser.prog}: {error}\n")
    print(f"Charts written to {image_dir}; counts written to {csv_dir}")


if __name__ == "__main__":
    main()
