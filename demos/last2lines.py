r"""
usage: python3.bash demos/last2lines.py bin/
"""

import __main__

import os
import pathlib
import sys


def main():

    assert sys.argv[1:]
    dir_path_name = sys.argv[1]

    assert not sys.argv[2:]

    main_name = __main__.__file__
    main_path = pathlib.Path(main_name)
    main_text = main_path.read_text()
    main_tail = "\n".join(main_text.splitlines()[-4:]) + "\n"

    for name in sorted(os.listdir(dir_path_name)):
        path_name = os.path.join(dir_path_name, name)
        assert "//" not in path_name, (path_name,)

        ext = os.path.splitext(path_name)[-1]
        if ext == ".py":
            path = pathlib.Path(path_name)
            text = path.read_text()
            tail = "\n".join(text.splitlines()[-4:]) + "\n"

            repl = main_tail.replace("demos/last2lines.py", path_name)
            if tail != repl:
                with open(path_name, "a") as appending:
                    appending.write(repl)


main()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/last2lines.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
