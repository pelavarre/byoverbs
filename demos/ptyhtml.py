import argparse
import os
import pty
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument("-a", dest="append", action="store_true")
parser.add_argument("-p", dest="use_python", action="store_true")
parser.add_argument("filename", nargs="?", default="typescript")
options = parser.parse_args()

shell = sys.executable if options.use_python else os.environ.get("SHELL", "sh")
filename = options.filename
mode = "ab" if options.append else "wb"

with open(filename, mode) as script:

    def read(fd):
        data = os.read(fd, 1024)
        script.write(data)
        return data

    print("Script started, file is", filename)
    script.write(("Script started on %s\n" % time.asctime()).encode())

    pty.spawn(shell, read)

    script.write(("Script done on %s\n" % time.asctime()).encode())
    print("Script done, file is", filename)


# above lines
# copied from Sun 7/May/2023 https://docs.python.org/3/library/pty.html
# then black'ened without adding/ deleting sourcelines


# usage:  python3 demos/ptyhtml.py [-h] [-a] [-p] [filename]


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/ptyhtml.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
