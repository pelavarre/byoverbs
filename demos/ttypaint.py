#!/usr/bin/env python3

r"""
usage: ttypaint.py [-h]

copy Bytes to Screen from Keyboard, like to make the Screen tell a better History

options:
  -h, --help  show this help message and exit

quirks:
  1 quits when told ⌃C ⌃M ⌃M ⌃M, or when told ⌃C ⇧Z⇧Q
  2 echoes Mouse Press/ Release as move Cursor
  3 loops Keystrokes to Terminal while Replacing/ Inserting, except ⌃C ⌃G ⌃M ⌃O ⌃V
  4 closely emulates Vi $ | 0 A H I J K L O R S X and ⇧4 ⇧\ and ⌃P ⌃N
  5 closely emulates Vi ⇧C ⇧D ⇧H ⇧L ⇧M ⇧O ⇧R ⇧S, also emulates ⇧X past first Column
  6 also emulates Vi + - ^ _ and ⇧I and ⇧= ⇧6 ⇧-, but can't see Dents

limits:
  can't read or search Chars, nor Dents, nor the Spaces beyond each End of Line
  can't save Changes, can't undo Changes, can't split Lines
  doesn't give you a cheatsheet of Terminal b'\e[1m' for Bold, b'\e34m' for Blue, etc

docs:
  https://en.wikipedia.org/wiki/ANSI_escape_code
  https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
  :!demos/ttypaint.py --  && : works to edit Vi Screen after Vi :set t_ti= t_te=

examples:
  ./demos/ttypaint.py --  # loop back like a Glass Terminal with no Remote Host
  ls -CR && ./demos/ttypaint.py --  # fill Screen with Text and then edit it
"""

# code reviewed by people, and by Black and Flake8


import __main__
import datetime as dt
import os
import re
import select
import shutil
import sys
import termios
import tty

_ = dt


#
# Run from the Sh command line
#


def main():
    """Run from the Sh command line"""

    if sys.argv[1:] != ["--"]:
        print(__main__.__doc__.strip())

        sys.exit(0)

    screen_edit_till()


def screen_edit_till():
    """Copy Keyboard to Screen, except for special cases"""

    stdio = sys.__stdout__  # '__stdout__' per 'shutil.get_terminal_size'
    with GlassTeletype(stdio) as gt:
        se = ScreenEditor(gt)
        try:
            while True:
                line = gt.readline()
                se.reply_to(line)
        finally:
            gt.write(b"\x1B[4l")  # CSI Pm l Reset Mode (RM)  # Ps 4 Insert Mode (IRM)
            gt.write(b"\x1B[ q")  # CSI Pm SP q Set Cursor Style (DECSCUSR)  # (default)

            se.to_lower_left()
            # gt.print()  # no, don't, let us quit without scrolling up


class ScreenEditor:
    """Copy Keyboard to Screen, except for special cases"""

    def __init__(self, gt):
        self.gt = gt

        self.fd = gt.fd
        self.input_lines = list()
        self.stdio = gt.stdio

        self.helping_bot_by_line = self.form_helping_bot_by_line()
        self.texting_bot_by_line = self.form_texting_bot_by_line()

        self.editing_start()

    def editing_start(self):
        """Start editing the Screen"""

        gt = self.gt

        _ = self.get_terminal_size()  # fails fast

        gt.print(
            "Press (⌃C and then) press Return (or ⌃M) three times to quit"
            " (or ⌃C L 0 Z Q)"
        )

        self.texting = None  # Texting False is Vi :stopinsert, not Vi :startinsert

    def get_terminal_size(self):
        """Count Columns and Rows of monospaced Terminal Screen Characters"""

        columns_lines = shutil.get_terminal_size()

        return columns_lines

    def to_lower_left(self):
        """Cursor Move to Lower Left"""

        assert CUP_Y_X == b"\x1B[{};{}H"

        (x, y) = self.get_terminal_size()

        x_ = 1
        self.write("\x1B[{};{}H".format(y, x_).encode())

    #
    # Take Keyboard Input Lines as saying more than they do
    #

    def reply_to(self, line):
        """Reply to 1 Keyboard Input Line"""

        helping_bot_by_line = self.helping_bot_by_line
        input_lines = self.input_lines
        texting_bot_by_line = self.texting_bot_by_line

        input_lines.append(line)

        #

        prefix = line[:1]

        bot = self.write
        if self.texting and (line == prefix):
            if prefix in texting_bot_by_line.keys():
                bot = texting_bot_by_line[prefix]
        else:
            if prefix in helping_bot_by_line.keys():
                bot = helping_bot_by_line[prefix]

        if False:  # jitter Sun 9/Apr
            if prefix != b"i":
                self.gt.__exit__()
                breakpoint()

        #

        bot(line)

        #

        if not self.texting:
            if input_lines[-3:] == [b"\r", b"\r", b"\r"]:
                sys.exit()
            if input_lines[-2:] == [b"Z", b"Q"]:
                sys.exit()

    def on_esc(self, line):
        r"""Reply to '\e' Keyboard Input Lines"""

        assert line.startswith(b"\x1B"), line

        if line.startswith(b"\x1B["):
            self.on_csi(line)
            return

        self.write(line)

    def on_csi(self, line):
        r"""Reply to '\e[' Keyboard Input Lines"""

        assert MouseButton == b"\x1B[" b"M"

        assert line.startswith(b"\x1B["), line

        if (len(line) == 6) and line.startswith(b"\x1B[" b"M"):
            self.on_mouse(line)
            return

        if re.match(rb"^\x1B\[([0-9]+);([0-9]+)R$", string=line):
            self.on_cpr(line)
            return

        self.write(line)

    def on_cpr(self, line):
        r"""Reply to '\e[...;...R' Cursor Position (CPR)"""

        m = re.match(rb"^\x1B\[([0-9]+);([0-9]+)R$", string=line)
        (ydigits, xdigits) = (m.group(1), m.group(2))
        (y, x) = (int(ydigits), int(xdigits))

        (columns, lines) = self.get_terminal_size()

        self.to_lower_left()
        self.write(b"\x1B[K")  # CSI Ps K  # Erase in Line (DECSEL)

        chars = '"/dev/tty" [Modified] {} lines {} columns   {},{}'.format(
            lines, columns, y, x
        )
        self.write(chars.encode())

        self.write("\x1B[{};{}H".format(y, x).encode())

    def on_mouse(self, line):
        r"""Reply to '\e[M' Keyboard Input Lines"""

        assert CUP_Y_X == b"\x1B[{};{}H"

        (cb, cx, cy) = (line[-3], line[-2], line[-1])

        _ = cb
        assert cx > 0x20, hex(cx)
        assert cy > 0x20, hex(cy)

        (x, y) = (cx - 0x20, cy - 0x20)

        self.write("\x1B[{};{}H".format(y, x).encode())

    def write(self, reply):
        """Write some Bytes without encoding them, and without adding an End to them"""

        gt = self.gt
        gt.write(reply)

    def texting_backup(self):
        """Back up the kind of Texting going on"""

        texting = self.texting
        assert texting in (None, "Inserting", "Replacing")

        return texting

    def texting_restore(self, texting, line):
        """Restore the kind of Texting going on"""

        if texting is None:
            self.helping_enter(line)
        elif texting == "Inserting":
            self.inserting_enter(line)
        else:
            assert texting == "Replacing"
            self.replacing_enter(line)

    #
    # Switch between Modes of Helping, Inserting, or Replacing
    #

    def helping_enter(self, line):  # Vi ⌃C
        """Stop texting, start helping"""

        self.texting = None

        self.write(b"\x1B[4l")  # CSI Pm l Reset Mode (RM)  # Ps 4 Insert Mode (IRM)
        self.write(b"\x1B[ q")  # CSI Pm SP q Set Cursor Style (DECSCUSR)  # (default)

        # todo: don't Reset Insert when not inserting

    def helping_visit(self, line):  # Vi ⌃O
        """Take one Keyboard Input Line as Helping"""

        gt = self.gt

        texting = self.texting_backup()
        self.helping_enter(line)

        inner_line = gt.readline()
        self.reply_to(inner_line)

        self.texting_restore(texting, line=line)

    def inserting_enter(self, line):  # Vi I
        """Tell the Screen to take Writes as Inserts, and stop helping"""

        self.texting = "Inserting"

        self.write(b"\x1B[4h")  # CSI Pm h Set Mode (SM)  # Ps 4 Insert Mode (IRM)
        self.write(b"\x1B[6 q")  # CSI Pm SP q Set Cursor Style (DECSCUSR)  # Steady Bar

    def right_and_inserting_enter(self, line):  # Vi A scrolls past last Column
        """Step right and tell the Screen to take Writes as Inserts, and stop helping"""

        self.write(b"\x1B[C")  # CSI Ps C Cursor Forward (CUF)
        self.inserting_enter(line)

    def inserting_enter_this(self, line):  # Vi ⇧I inserts past Dent
        """Slam left and tell the Screen to take Writes as Inserts, and stop helping"""

        self.write(b"\r")
        self.inserting_enter(line)

    def replacing_enter(self, line):  # Vi ⇧R
        """Tell the Screen to take Writes as Overwrites, and stop helping"""

        self.texting = "Replacing"

        self.write(b"\x1B[4l")  # CSI Pm l Reset Mode (RM)  # Ps 4 Insert Mode (IRM)
        self.write(
            b"\x1B[4 q"
        )  # CSI Pm SP q Set Cursor Style (DECSCUSR)  # Steady Line

    def replacing_visit(self, line):  # Vi R
        """Take one Keyboard Input Line as Replacing"""

        gt = self.gt

        texting = self.texting_backup()
        self.replacing_enter(line)

        inner_line = gt.readline()
        self.reply_to(inner_line)

        self.texting_restore(texting, line=line)

    def writing_visit(self, line):  # Vi ⌃V
        """Take one Keyboard Input Line as Writing unchanged, directly, to Screen"""

        gt = self.gt

        texting = self.texting_backup()
        self.replacing_enter(line)

        inner_line = gt.readline()
        self.write(inner_line)

        self.texting_restore(texting, line=line)

    def write_device_status_report(self, line):  # Vi ⌃G
        """Call for b'\x1B[{y};{x}R' Cursor Position (CPR)"""

        self.write(b"\x1B[6n")  # CSI Ps n Device Status Report (DSR)

    #
    # Move the Cursor relatively
    #

    def to_column_left(self, line):  # Vi H
        """Cursor Move Left"""

        self.write(b"\b")

    def to_column_right(self, line):  # Vi L stops on Last Char in Line
        """Cursor Move Right"""

        self.write(b"\x1B[C")

    def to_row_down(self, line):  # Vi J  # Vi ⌃N  # Vi ⇧= + goes past Dent
        """Cursor Move Down"""

        self.write(b"\x1B[B")

    def to_row_up(self, line):  # Vi K  # Vi ⌃P  # Vi - goes past Dent
        """Cursor Move Up"""

        self.write(b"\x1B[A")

    #
    # Move the Cursor absolutely
    #

    def to_column_chosen(self, line):  # Vi ⇧\ |  # Vi 0  # Vi ⇧- _ goes past Dent
        """Cursor Move to chosen Column of Row"""

        self.write(b"\r")

    def to_column_beyond(self, line):  # Vi ⇧4  # Vi $ goes to past last Char in Row
        """Cursor Move to last Column of Row"""

        (x, y) = self.get_terminal_size()
        reply = "\x1B[{}G".format(x).encode()  # CSI Ps G  # Cursor Char Absolute (CHA)
        os.write(sys.__stdout__.fileno(), reply)

    def to_row_first(self, line):  # Vi ⇧H goes to first Row, past Dent
        """Cursor Move to first Row of Screen"""

        self.write(b"\x1B[d")  # CSI Ps d  # Line Position Absolute

    def to_row_middle(self, line):  # Vi ⇧M goes to middle Row, past Dent
        """Cursor Move to middle Row of Screen"""

        (x, y) = self.get_terminal_size()
        reply = "\x1B[{}d".format(y // 2).encode()  # CSI Ps d  # Line Pos Abs
        os.write(sys.__stdout__.fileno(), reply)

    def to_row_last(self, line):  # Vi ⇧L goes to last Row, past Dent
        """Cursor Move to last Row of Screen"""

        (x, y) = self.get_terminal_size()
        reply = "\x1B[{}d".format(y).encode()  # CSI Ps d  # Line Pos Abs
        os.write(sys.__stdout__.fileno(), reply)

    def to_row_this(self, line):  # Vi ⇧6 ^ goes past Dent
        """Cursor Move to first Column of Row"""

        self.write(b"\r")

    #
    # Move a little or not at all, and delete or insert or both
    #

    def char_change_to_beyond(self, line):  # Vi ⇧C
        """Char Delete to beyond last Char of Line and start Inserting"""

        self.write(b"\x1B[K")  # CSI Ps K  # Erase in Line (DECSEL)

        self.inserting_enter(line)

    def char_change_right(self, line):  # Vi S
        """Char Delete Right and start Inserting"""

        self.write(b"\x1B[P")  # CSI Ps P  # Delete Characters (DCH)

        self.inserting_enter(line)

    def char_delete_left(self, line):  # Vi ⇧X deletes nothing from the first Column
        """Char Delete Left"""

        self.write(b"\b")
        self.write(b"\x1B[P")  # CSI Ps P  # Delete Characters (DCH)

    def char_delete_right(self, line):  # Vi X
        """Char Delete Right"""

        self.write(b"\x1B[P")  # CSI Ps P  # Delete Characters (DCH)

    def char_delete_to_beyond(self, line):  # Vi ⇧D
        """Char Delete to beyond last Char of Line"""

        self.write(b"\x1B[K")  # CSI Ps K  # Erase in Line (DECSEL)
        self.write(b"\b")

    def char_insert_line_break(self, line):  # Vi ⌃M Return splits the Line
        """Split the Line"""

        self.write(b"\x1B[K")  # CSI Ps K  # Erase in Line (DECSEL)
        self.write(b"\r\n")
        self.line_insert_above(line)

    def line_change_this(self, line):  # Vi S
        """Char Delete Right and start Inserting"""

        self.write(b"\r")
        self.write(b"\x1B[K")  # CSI Ps K  # Erase in Line (DECSEL)

        self.inserting_enter(line)

    def line_insert_above(self, line):  # Vi ⇧O
        """Insert Line Above"""

        self.write(b"\x1B[L")  # CSI Ps L  # Insert Lines (IL)
        self.write(b"\r")

        self.inserting_enter(line)

    def line_insert_below(self, line):  # Vi O
        """Insert Line Below"""

        self.write(b"\r\n")

        self.line_insert_above(line)

    #
    # Map Keyboard Input Lines to Editor Action while Helping
    #

    def form_helping_bot_by_line(self):
        """Say how to cook Keyboard Input Lines while not Replacing/ Inserting"""

        bot_by_line = dict()

        # Vi ⌃⇧2, Vi ⌃A, Vi ⌃B, Vi ⌃C, Vi ⌃D
        # todo: ⌃E scroll up
        # Vi ⌃F
        bot_by_line[b"\x07"] = self.write_device_status_report  # Vi ⌃G
        # Vi ⌃H works when echoed as Backspace BS
        # Vi ⌃V⌃I works when echoed
        # todo: ⌃I Tab and b'\e[Z' Shift-Tab
        # Vi ⌃V⌃J works when echoed (including scroll up 1 row when at last row)
        # Vi ⌃K works when echoed (as Vertical Tab VT alias of ⌃J Line Feed LF)
        # Vi ⌃L
        # Vi ⌃M works when echoed as Carriage Return CR
        bot_by_line[b"\x0E"] = self.to_row_down  # Vi ⌃N
        # Vi ⌃O
        bot_by_line[b"\x10"] = self.to_row_up  # Vi ⌃P
        # Vi ⌃Q, Vi ⌃R, Vi ⌃S, Vi ⌃T, Vi ⌃U
        # todo: ⌃V Alt Editing Flavor ⌃V
        # Vi ⌃W, Vi ⌃X, Vi ⌃Y, Vi ⌃Z

        bot_by_line[b"\x1B"] = self.on_esc  # Vi ⌃[
        # Vi ⌃[, Vi ⌃\, Vi ⌃], Vi ⌃^, Vi ⌃_, Vi ⌃`

        # Vi Space, Vi !, Vi ", Vi #
        bot_by_line[b"$"] = self.to_column_beyond  # Vi ⇧4  # Vi $
        # Vi %, Vi &
        # todo: ' as go to Mark
        # Vi (, Vi ), Vi *
        bot_by_line[b"+"] = self.to_row_down  # Vi ⇧=  # Vi +
        # Vi ,
        bot_by_line[b"-"] = self.to_row_up  # Vi -
        # todo: Vi . as Repeat
        # Vi /

        bot_by_line[b"0"] = self.to_column_chosen  # Vi 0
        # TODO: 0123456789 as Choose Count
        # Vi :, Vi ;
        # TODO: <L as Undent  # Vi << stops undenting after Dent
        # Vi =
        # TODO: >L as Dent  # Vi >> doesn't delete Chars scrolled off Screen
        # Vi ?

        # Vi ⇧A
        # Vi ⇧B
        bot_by_line[b"C"] = self.char_change_to_beyond  # Vi ⇧C
        bot_by_line[b"D"] = self.char_delete_to_beyond  # Vi ⇧D
        # Vi ⇧E
        # Vi ⇧F
        # Vi ⇧G
        bot_by_line[b"H"] = self.to_row_first  # Vi ⇧H
        bot_by_line[b"I"] = self.inserting_enter_this  # Vi ⇧I
        # Vi ⇧J
        # Vi ⇧K
        bot_by_line[b"L"] = self.to_row_last  # Vi ⇧L
        bot_by_line[b"M"] = self.to_row_middle  # Vi ⇧M
        # Vi ⇧N
        bot_by_line[b"O"] = self.line_insert_above  # Vi ⇧O
        # Vi ⇧P
        # Vi ⇧Q
        bot_by_line[b"R"] = self.replacing_enter  # Vi ⇧R
        bot_by_line[b"S"] = self.line_change_this  # Vi ⇧S
        # Vi ⇧T
        # Vi ⇧U
        # todo: Vi ⇧V as Alt Editing Flavor ⇧V
        # Vi ⇧W
        bot_by_line[b"X"] = self.char_delete_left  # Vi ⇧X
        # Vi ⇧Y
        # Vi ⇧Z

        # Vi [, Vi \, Vi ]
        bot_by_line[b"^"] = self.to_row_this
        bot_by_line[b"_"] = self.to_column_chosen
        # todo: Vi ` for go to Mark

        bot_by_line[b"a"] = self.right_and_inserting_enter
        # Vi B
        # todo: CC like ⇧S
        # todo: DD for Line Delete without Inserting Enter
        # Vi E
        # Vi F
        # Vi G
        bot_by_line[b"h"] = self.to_column_left  # Vi H
        bot_by_line[b"i"] = self.inserting_enter  # Vi I
        bot_by_line[b"j"] = self.to_row_down  # Vi J
        bot_by_line[b"k"] = self.to_row_up  # Vi K
        bot_by_line[b"l"] = self.to_column_right  # Vi L
        # todo: M for placing Mark
        # Vi N
        bot_by_line[b"o"] = self.line_insert_below  # Vi O
        # Vi P
        # todo: Q for record/ replay of Keystroke Input Lines
        bot_by_line[b"r"] = self.replacing_visit  # Vi R
        bot_by_line[b"s"] = self.char_change_right  # Vi S
        # Vi T
        # Vi U
        # todo: V as Alt Editing Flavor V
        # Vi W
        bot_by_line[b"x"] = self.char_delete_right
        # Vi Y
        # todo: Z as Scroll This Line to ZB ZT ZZ

        # Vi {
        bot_by_line[b"|"] = self.to_column_chosen
        # Vi }
        # Vi ~

        return bot_by_line

    #
    # Map Keyboard Input Lines to Editor Action while Replacing/ Inserting
    #

    def form_texting_bot_by_line(self):
        """Say how to cook Keyboard Input Lines while Replacing/ Inserting"""

        bot_by_line = dict()

        bot_by_line[b"\x03"] = self.helping_enter  # Vi ⌃C
        bot_by_line[b"\x07"] = self.write_device_status_report  # Vi ⌃G
        bot_by_line[b"\x0D"] = self.char_insert_line_break  # Vi ⌃M Return
        bot_by_line[b"\x0F"] = self.helping_visit  # Vi ⌃O
        bot_by_line[b"\x16"] = self.writing_visit  # Vi ⌃V

        return bot_by_line


class GlassTeletype:
    """Read from Keyboard, write to Screen, but don't line-buffer the Keyboard Input"""

    def __init__(self, stdio):
        self.stdio = stdio
        self.fd = stdio.fileno()
        self.line = bytearray()

    def __enter__(self):
        """Stop streaming Lines in from the Keyboard, start streaming Bytes in"""

        fd = self.fd

        assert MouseEnter == b"\x1B[" b"?1000h"
        assert PasteEnter == b"\x1B[" b"?2004h"

        tcgetattr = termios.tcgetattr(fd)
        tty.setraw(fd, when=termios.TCSADRAIN)  # Drain flushes Output, then changes
        # termios.TCSAFLUSH  # Flush destroys Input, flushes Output, then changes

        os.write(fd, b"\x1B[" b"?2004h")
        os.write(fd, b"\x1B[" b"?1000h")

        self.tcgetattr = tcgetattr

        return self

        # also stop adding "\r" before each "\n" of Output

    def __exit__(self, *exc_info):
        """Stop streaming Bytes in from the Keyboard, restart streaming Lines in"""

        fd = self.fd
        tcgetattr = self.tcgetattr

        assert MouseExit == b"\x1B[" b"?1000l"
        assert PasteExit == b"\x1B[" b"?2004l"

        os.write(fd, b"\x1B[" b"?1000l")
        os.write(fd, b"\x1B[" b"?2004l")

        when = termios.TCSADRAIN
        termios.tcsetattr(fd, when, tcgetattr)

        # also restart adding "\r" before each "\n" of Output

    def print(self, *args, **kwargs):
        """Work like Print, but default to end with '\r\n', not with '\n'"""

        alt_kwargs = dict(kwargs)
        if ("end" not in kwargs) or (kwargs["end"] is None):
            alt_kwargs["end"] = "\r\n"

        print(*args, **alt_kwargs)

    def write(self, line):
        """Write some Bytes without encoding them, and without adding an End to them"""

        fd = self.fd

        os.write(fd, line)

    def readline(self):
        """Read the next Keyboard Input struck or pasted"""

        fd = self.fd
        line = self.line

        # Return the next whole Chunk of Paste or Key Stroke

        while True:
            (stroke, lookahead) = bytes_splitstroke(line)
            if stroke:
                line[::] = lookahead
                return stroke

            # Else read many Bytes pasted in a rush, or a few, or one

            length = 1500  # 2023-03 macOS yielded 1022 Bytes per call
            timeout = 125e-3

            while True:
                read = os.read(fd, length)
                line.extend(read)

                if len(read) >= 1000:
                    if self.kbhit(timeout):
                        continue
                break

    def kbhit(self, timeout):  # 'timeout' in seconds
        """Wait till next Keyboard Input struck or pasted, or Timeout"""

        rlist = [self.stdio]
        wlist = list()
        xlist = list()

        (rlist_, _, _) = select.select(rlist, wlist, xlist, timeout)

        return rlist_  # emptied after Timeout, else copied 'rlist'


def bytes_splitstroke(line):
    """Pick out the next whole Chunk of Paste or Key Stroke"""

    assert MouseButton == b"\x1B[" b"M"

    stroke = line
    lookahead = b""

    if len(line) >= 6:
        if line.startswith(b"\x1B[" b"M"):
            stroke = line[:6]
            lookahead = line[6:]

    stroke = bytes(stroke)
    lookahead = bytes(lookahead)

    return (stroke, lookahead)


#
# Decipher Terminal Byte Codes, written or read
#

Esc = b"\x1B"

CSI = b"\x1B["


#
# Decipher Keyboard Byte Codes, mostly read and rarely written
#


CPR = b"\x1B[{};{}R"  # Cursor Position Report (CPR) of Row Y Column X in reply to DSR

MouseButton = b"\x1B[" b"M"


#
# Decipher Screen Byte Codes, mostly written and rarely read
#


CUP_Y_X = b"\x1B[{};{}H"  # Cursor Position (CUP) to move Cursor to Row Y Column X

DSR = b"\x1B[" b"6n"  # Device Status Report (DSR) call for CPR

MouseEnter = b"\x1B[" b"?1000h"  # CSI ? Pm h  # Ps = 1 0 0 0  # SET_VT200_MOUSE
MouseExit = b"\x1B[" b"?1000l"  # CSI ? Pm l  # Ps = 1 0 0 0  # SET_VT200_MOUSE

PasteEnter = b"\x1B[" b"?2004h"  # CSI ? Pm h  # Ps = 2 0 0 4
PasteExit = b"\x1B[" b"?2004l"  # CSI ? Pm l  # Ps = 2 0 0 4


#
# Run from the Sh command line, when not imported
#


if __name__ == "__main__":
    main()


# todo: define '--no-banner' to not even scroll up Two Lines
# todo: Mouse Drag to feed into 'pbcopy'


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/demos/ttypaint.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
