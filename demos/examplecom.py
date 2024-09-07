#!/usr/bin/env python3


import pathlib
import subprocess
import sys
import unicodedata


SLACK_NAME_TO_UNICODE = {
    "black_circle": "Medium Black Circle",  # not Large
    "large_blue_circle": "Large Blue Circle",
    "large_green_circle": "Large Green Circle",
    "mag": "Left-Pointing Magnifying Glass",
    "no_entry_sign": "No Entry Sign",
    "red_circle": "Large Red Circle",
    "white_check_mark": "White Heavy Check Mark",  # white-on-green
    "zzz": "Sleeping Symbol",
}


def main() -> None:
    itty = sys.stdin.isatty()
    otty = sys.stdin.isatty()

    # Copy Input to Sponge

    if not itty:
        istr = pathlib.Path("/dev/stdin").read_text(errors="surrogateescape")
    else:  # 'pbpaste' commonly available at macOS
        run = subprocess.run(
            "pbpaste".split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            errors="surrogateescape",
            check=True,
        )
        istr = run.stdout

    # Edit the Str captured by Sponge

    ostr = str_to_str(istr)

    # Copy Sponge to Output

    if not otty:
        pathlib.Path("/dev/stdout").write_text(ostr, errors="surrogateescape")
    else:  # 'pbcopy' commonly available at macOS
        subprocess.run("pbcopy".split(), input=ostr, errors="surrogateescape", check=True)


def str_to_str(istr) -> str:
    """Copy Str, but filter its bits as we go"""

    ostr = istr

    # breakpoint() # jitter Sun 15/Oct

    for sname, uname in SLACK_NAME_TO_UNICODE.items():
        smarkup = ":{}:".format(sname)
        utext = unicodedata.lookup(uname)

        ostr = ostr.replace(smarkup, utext)

    return ostr


main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/examplecom.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
