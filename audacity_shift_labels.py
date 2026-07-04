#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///

import argparse
from typing import Generator

SECONDS_PER_MINUTE = 60


def parse_time(time_str: str) -> float:
    """
    Parse an offset given either as plain (decimal) seconds or as H:M:S.

    A colon triggers H:M:S parsing: the hours/minutes components are integers
    and the seconds component is a decimal fraction, so "1:52.5" is 112.5s and
    "1:23:45.678" is 5025.678s. Without a colon the string is parsed as plain
    decimal seconds (".3" -> 0.3). A leading "-" negates the whole value.

    Args:
        time_str (str): The offset, e.g. "0.3", "-.3", "1:52.216", "1:23:45.678".

    Returns:
        float: The offset in seconds.
    """
    negative = time_str.startswith("-")
    if negative:
        time_str = time_str[1:]

    if ":" in time_str:
        components = time_str.split(":")
        value = float(components[-1])
        for power, component in enumerate(reversed(components[:-1]), start=1):
            value += int(component) * SECONDS_PER_MINUTE**power
    else:
        value = float(time_str)

    return -value if negative else value


def read_file_as_generator(filename: str) -> Generator[str, None, None]:
    """
    Generator that reads a file line by line.

    Args:
        filename (str): The path to the input file.

    Yields:
        str: Each line from the input file.
    """
    with open(filename, "r") as file:
        for line in file:
            yield line


def shift_labels(
    lines: Generator[str, None, None], offset: float, clamp: bool = False
) -> Generator[str, None, None]:
    """
    Shift the labels (or numbers) in the input lines by the given offset.

    Args:
        lines (Generator): Generator yielding lines from the input file.
        offset (float): The amount by which to shift the labels.
        clamp (bool): When True, clamp shifted times to a minimum of 0
            (never emit negative times).

    Yields:
        str: The shifted labels as strings.
    """

    def shift(value: str) -> float:
        shifted = float(value) + offset
        return max(0.0, shifted) if clamp else shifted

    for line in lines:
        try:
            # Split the line by tabs (since Audacity label format uses tabs).
            parts = line.strip("\n").split("\t")

            # Check how many parts are present and apply logic accordingly.
            if len(parts) == 1:  # One time no label case.
                start_time = shift(parts[0])
                yield f"{start_time:.6f}\t\n"
            elif len(parts) == 2:  # One time + label case.
                start_time = shift(parts[0])
                label = parts[1]
                yield f"{start_time:.6f}\t{label}\n"
            elif len(parts) >= 3:  # Start time, end time, and label.
                start_time = shift(parts[0])
                end_time = shift(parts[1])
                label = "\t".join(
                    parts[2:]
                )  # Join everything after time columns as the label
                yield f"{start_time:.6f}\t{end_time:.6f}\t{label}\n"
            else:
                raise ValueError(f"Unexpected format in line: {line.strip()}")
        except ValueError as e:
            # If conversion to float fails or unexpected format occurs, log the error
            yield f"Error processing line: {line.strip()} - {str(e)}\n"


def main(argv=None):
    """
    Command-line interface that reads an input file, shifts the labels by the given offset,
    and either modifies the file in place or prints the result to standard output.
    """
    parser = argparse.ArgumentParser(description=main.__doc__.strip())
    parser.add_argument(
        "input_filename",
        help="File containing audacity labels or a column of numbers",
    )
    parser.add_argument(
        "offset",
        help="Offset by which to shift the labels, as seconds (e.g. .3, -.3) "
        "or HH:MM:SS (e.g. 1:52.216, 1:23:45.678)",
    )
    parser.add_argument(
        "-i",
        "--inplace",
        action="store_true",
        help="Modify the input file in place",
    )
    parser.add_argument(
        "-c",
        "--clamp",
        action="store_true",
        help="Clamp shifted times to a minimum of 0",
    )
    args = parser.parse_args(argv)

    # list defies generator, but otherwise it doesn't work, because the file is
    # truncated before generator had a chance to read:
    lines = list(read_file_as_generator(args.input_filename))

    shifted_labels = shift_labels(lines, parse_time(args.offset), clamp=args.clamp)

    if args.inplace:
        with open(args.input_filename, "w") as file:
            for label in shifted_labels:
                file.write(label)
    else:
        for label in shifted_labels:
            print(label, end="")


if __name__ == "__main__":
    main()
