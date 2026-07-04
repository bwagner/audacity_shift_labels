# test_audacity_shift_labels.py


import pytest

from audacity_shift_labels import parse_time, shift_labels


@pytest.mark.parametrize(
    "time_str, expected",
    [
        # H:M:S.ms (colon present -> hours/minutes int, seconds decimal)
        ("01:52.216", 112.216),
        ("1:23:45.678", 5025.678),
        ("-1:23:45.678", -5025.678),
        # colon form with a non-3-digit fraction reads as decimal seconds
        ("1:52.5", 112.5),
        # bare decimals stay plain seconds (existing CLI behaviour)
        ("30.123", 30.123),
        ("-30.456", -30.456),
        (".3", 0.3),
        ("-.3", -0.3),
        ("0", 0.0),
    ],
)
def test_parse_time(time_str, expected):
    assert parse_time(time_str) == pytest.approx(expected)


def test_parse_time_invalid():
    with pytest.raises(ValueError):
        parse_time("invalid time")


@pytest.mark.parametrize(
    "input_lines, offset, expected_output",
    [
        # start+end both shift below zero -> clamped to 0
        (
            ["1.000000\t3.000000\tLabel A\n"],
            -5.0,
            ["0.000000\t0.000000\tLabel A\n"],
        ),
        # one column (single time) clamped
        (
            ["2.000000\n"],
            -5.0,
            ["0.000000\t\n"],
        ),
        # time + label clamped
        (
            ["2.000000\tLabel B\n"],
            -5.0,
            ["0.000000\tLabel B\n"],
        ),
        # positive results are untouched by clamping
        (
            ["1.000000\t3.000000\tLabel A\n"],
            0.5,
            ["1.500000\t3.500000\tLabel A\n"],
        ),
    ],
)
def test_shift_labels_clamp(input_lines, offset, expected_output):
    output = list(shift_labels((line for line in input_lines), offset, clamp=True))
    assert output == expected_output


def test_shift_labels_default_allows_negative():
    # default (clamp=False) still emits negative times
    output = list(shift_labels(iter(["1.000000\t3.000000\tLabel A\n"]), -5.0))
    assert output == ["-4.000000\t-2.000000\tLabel A\n"]


@pytest.mark.parametrize(
    "input_lines, offset, expected_output",
    [
        # single column input (start time + label)
        (
            ["1.000000\tLabel A\n", "2.500000\tLabel B\n"],
            0.5,
            ["1.500000\tLabel A\n", "3.000000\tLabel B\n"],
        ),
        # two columns (start time, end time + label)
        (
            ["1.000000\t2.000000\tLabel A\n", "3.500000\t5.000000\tLabel B\n"],
            0.5,
            ["1.500000\t2.500000\tLabel A\n", "4.000000\t5.500000\tLabel B\n"],
        ),
        # empty labels (just time values, no actual label)
        (
            ["1.000000\t2.000000\t\n", "3.500000\t4.500000\t\n"],
            0.5,
            ["1.500000\t2.500000\t\n", "4.000000\t5.000000\t\n"],
        ),
        # negative offset
        (
            ["1.000000\t3.000000\tLabel A\n", "4.500000\tLabel B\n"],
            -0.5,
            ["0.500000\t2.500000\tLabel A\n", "4.000000\tLabel B\n"],
        ),
        # one column (single time value)
        (
            ["1.000000\n", "2.500000\n"],
            0.5,
            ["1.500000\t\n", "3.000000\t\n"],
        ),
        # zero offset
        (
            ["1.000000\t3.000000\tLabel A\n", "4.500000\tLabel B\n"],
            0.0,
            ["1.000000\t3.000000\tLabel A\n", "4.500000\tLabel B\n"],
        ),
    ],
)
def test_shift_labels(input_lines, offset, expected_output):
    # Simulate input as a generator
    input_gen = (line for line in input_lines)

    # Call shift_labels and collect output
    output_gen = shift_labels(input_gen, offset)
    output_lines = list(output_gen)

    # Check if the output matches the expected output
    assert output_lines == expected_output


@pytest.mark.parametrize(
    "input_lines, offset, expected_errors",
    [
        # invalid time format (non-numeric)
        (
            ["InvalidTime\t2.000000\tLabel A\n", "3.500000\tInvalidEnd\tLabel B\n"],
            0.5,
            [
                "Error processing line: InvalidTime\t2.000000\tLabel A - could not convert string to float: 'InvalidTime'\n",
                "Error processing line: 3.500000\tInvalidEnd\tLabel B - could not convert string to float: 'InvalidEnd'\n",
            ],
        ),
        # missing time column (too few columns)
        (
            ["\tLabel A\n", "3.500000\t\tLabel B\n"],
            0.5,
            [
                "Error processing line: Label A - could not convert string to float: ''\n",
                "Error processing line: 3.500000\t\tLabel B - could not convert string to float: ''\n",
            ],
        ),
    ],
)
def test_shift_labels_invalid_input(input_lines, offset, expected_errors):
    # Simulate input as a generator
    input_gen = (line for line in input_lines)

    # Call shift_labels and collect output
    output_gen = shift_labels(input_gen, offset)
    output_lines = list(output_gen)

    # Check if the output contains expected error messages
    assert output_lines == expected_errors
