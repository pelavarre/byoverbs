import select
import sys
import termios
import time
import tty


def kbhit(timeout=None) -> bool:  # 'timeout' in seconds
    """Wait till next Input Byte, else till Timeout, else till forever"""

    fd = sys.stdin.fileno()

    rlist: list[int] = [fd]
    wlist: list[int] = list()
    xlist: list[int] = list()

    (alt_rlist, _, _) = select.select(rlist, wlist, xlist, timeout)
    hit = bool(alt_rlist)

    return hit


fd = sys.stdin.fileno()
tcgetattr = termios.tcgetattr(fd)
tty.setraw(fd, when=termios.TCSADRAIN)  # SetRaw defaults to TcsaFlush
try:
    for index in range(10):
        print(index, kbhit(timeout=0), end="\r\n")
        time.sleep(0.3)
finally:
    when = termios.TCSADRAIN
    termios.tcsetattr(fd, when, tcgetattr)


# Mar/2024 ReplIt·Com Console could NOT do this TermIOs Select kind of 'kbhit()'
# Mar/2024 ReplIt·Com Shell could do this TermIOs Select kind of 'kbhit()'


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/kbhit.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
