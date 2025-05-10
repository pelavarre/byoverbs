"""
usage: main.py

move a colored ball back and forth a few times

examples:
  clear
  python3 main.py
"""

import time

#
# Configure
#

X_LIST = (2 * [3, 6, 9, 12, 15, 12, 9, 6]) + [3]

NoBall = " "
GreenBall = "\N{LARGE GREEN CIRCLE}"
EmptyRow = (max(X_LIST) + 1) * NoBall

#
# Run
#

print()
print("Hello")
print("Let's try forward, back, forward, back, done")
print()

print("\x1b[?25l")  # DecCsiCursorHide

x_list = list(X_LIST)

erase = ""
while x_list:
    x = x_list.pop()

    plot = EmptyRow[: x - 1] + GreenBall
    print("\r" + erase + "\r" + plot, end="")

    time.sleep(0.2)

    erase = EmptyRow[: x - 1] + NoBall

print("\n", end="")

print("\x1b[?25h")  # DecCsiCursorShow

print()
print("Ta da")
print()
