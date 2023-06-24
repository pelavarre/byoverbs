import sys


def main():
    assert not sys.argv[1:], (sys.argv[0], sys.argv[1:])

    print("bash --noprofile --norc")
    print("exit 3")
    print("zsh -f")
