#!/usr/bin/env python

from typing import Generator


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
    lines: Generator[str, None, None], offset: float
) -> Generator[str, None, None]:
    """
    Shift the labels (or numbers) in the input lines by the given offset.

    Args:
        lines (Generator): Generator yielding lines from the input file.
        offset (float): The amount by which to shift the labels.

    Yields:
        str: The shifted labels as strings.
    """
    for line in lines:
        try:
            # Split the line by tabs (since Audacity label format uses tabs).
            parts = line.strip("\n").split("\t")

            # Check how many parts are present and apply logic accordingly.
            if len(parts) == 1:  # One time no label case.
                start_time = float(parts[0]) + offset
                yield f"{start_time:.6f}\t\n"
            elif len(parts) == 2:  # One time + label case.
                start_time = float(parts[0]) + offset
                label = parts[1]
                yield f"{start_time:.6f}\t{label}\n"
            elif len(parts) >= 3:  # Start time, end time, and label.
                start_time = float(parts[0]) + offset
                end_time = float(parts[1]) + offset
                label = "\t".join(
                    parts[2:]
                )  # Join everything after time columns as the label
                yield f"{start_time:.6f}\t{end_time:.6f}\t{label}\n"
            else:
                raise ValueError(f"Unexpected format in line: {line.strip()}")
        except ValueError as e:
            # If conversion to float fails or unexpected format occurs, log the error
            yield f"Error processing line: {line.strip()} - {str(e)}\n"


if __name__ == "__main__":
    import typer

    def main(
        input_filename: str = typer.Argument(
            ..., help="File containing audacity labels or a column of numbers"
        ),
        offset: float = typer.Argument(..., help="Offset by which to shift the labels"),
        inplace: bool = typer.Option(
            False, "--inplace", "-i", help="Modify the input file in place"
        ),
    ):
        """
        Command-line interface that reads an input file, shifts the labels by the given offset,
        and either modifies the file in place or prints the result to standard output.
        """
        # list defies generator, but otherwise it doesn't work, because the file is
        # truncated before generator had a chance to read:
        lines = list(read_file_as_generator(input_filename))

        shifted_labels = shift_labels(lines, offset)

        if inplace:
            with open(input_filename, "w") as file:
                for label in shifted_labels:
                    file.write(label)
        else:
            for label in shifted_labels:
                print(label, end="")

    typer.run(main)
