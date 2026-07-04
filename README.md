# audacity_shift_labels

Shifts [Audacity](https://www.audacityteam.org/) labels by a (possibly negative) offset.
```console
usage: audacity_shift_labels [-h] [-i] [-c] input_filename offset

Command-line interface that reads an input file, shifts the labels by the
given offset, and either modifies the file in place or prints the result to
standard output.

positional arguments:
  input_filename  File containing audacity labels or a column of numbers
  offset          Offset by which to shift the labels, as seconds (e.g. .3,
                  -.3) or HH:MM:SS (e.g. 1:52.216, 1:23:45.678)

options:
  -h, --help      show this help message and exit
  -i, --inplace   Modify the input file in place
  -c, --clamp     Clamp shifted times to a minimum of 0
```
Example invocation (I want to shift labels by .3 seconds)
```console
audacity_shift_labels.py labels.txt .3 > new_labels.txt
```
The offset may also be given as `HH:MM:SS`, where the seconds component is a
decimal fraction:
```console
audacity_shift_labels.py labels.txt 1:52.216 > new_labels.txt   # +112.216 seconds
```
Note: A negative `HH:MM:SS` offset looks like an option, so precede it with `--`
(plain negative seconds like `-.3` are recognized as a number and don't need it):
```console
audacity_shift_labels.py labels.txt -- -1:0:0 > new_labels.txt  # -1 hour
```
Pass `--clamp`/`-c` to keep shifted times from going below zero (any negative
result is clamped to `0`):
```console
audacity_shift_labels.py labels.txt --clamp -- -5 > new_labels.txt
```

## See also
- [rebuildap](https://github.com/bwagner/rebuildap)
- [audacity_click_label](https://github.com/bwagner/audacity_click_label)
- [quantize_labels](https://github.com/bwagner/quantize_labels)
- [beats2bars](https://github.com/bwagner/beats2bars)
- [audacity_legatize](https://github.com/bwagner/audacity_legatize)
- [pyaudacity](https://github.com/bwagner/pyaudacity)
