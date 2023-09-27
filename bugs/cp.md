# bugs/cp.md

Classic Cp shoves on you,<br>
( a ) to pick an old Filename to copy from,<br>
( b ) to pick a new Filename to copy to,<br>
( c ) to say '-i' to stop losing old Files as often as your new Filename isn't new,
and <br>
( d ) to say '-p' to copy the last-modified date/time-stamp.

Cp·Py does better, unless you say different.<br>
( a ) Cp·Py copies from the last-modified File.<br>
( b ) Cp·Py chooses a new Filename like Emacs does for Backup Copies.<br>
( c ) Cp·Py fails when your new Filename isn't new.<br>
( d ) Cp·Py leaves the File stamped as last-modified when it was last-modified.

Cp·Py with no arguments gives you examples to copy-edit,
examples of making Cp·Py do as well.

Tests

    cp.py
    touch t.txt
    cp.py --  # once
    cp.py --  # again

## Copied from

Posted into:  https://github.com/pelavarre/byoverbs/blob/main/bugs/cp.md
<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git
