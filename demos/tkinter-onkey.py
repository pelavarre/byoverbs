#!/usr/bin/env python3

r"""
usage: tkinter-onkey.py [-h] [--yolo]

change the Turtle Screen BgColor to a Hash of the Key Cap

options:
  -h, --help  show this help message and exit
  --yolo      do what's popular now

examples:
  ./demos/tkinter-onkey.py --yolo
  cd demos/
  python3 tkinter-onkey.py --yolo
  python3 <(curl -Ss https://raw.githubusercontent.com/pelavarre/byoverbs/refs/heads/main/demos/tkinter-onkey.py) --yolo
"""

# code reviewed by People, Black, Flake8, MyPy, & PyLance-Standard


import hashlib
import turtle  # gCloud Shell raises ModuleNotFoundError: No module named 'tkinter'


#
# Run from the Sh command line
#


def main() -> None:

    # assert sys.argv[1:] == ["--yolo"], (sys.argv[1:],)

    t = turtle.Turtle()
    ts = t.screen

    for code in range(0x20, 0x7E + 1):
        ch = chr(code)

        hasher = hashlib.md5()
        hasher.update(ch.encode())
        digest = hasher.digest()

        hcolor = f"#{digest[0]:02X}{digest[1]:02X}{digest[2]:02X}"

        def func(_ch=ch, _code=code, _hcolor=hcolor) -> None:
            print(_code, repr(_ch), _hcolor, end="\r\n")
            ts.bgcolor(_hcolor)

        ts.onkey(func, ch)

    ts.listen()
    ts.mainloop()


#
# Run from the Sh command line, when not imported
#


if __name__ == "__main__":
    main()


# todo: rewrite the declarations of Global Variables to conform to PyLance Standard


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/demos/tkinter-onkey.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
