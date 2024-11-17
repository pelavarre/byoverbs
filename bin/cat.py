_ = r"""

% diff -brpu pelavarre/byobash/bin/cat.py byoverbs/bin/cat.py
--- pelavarre/byobash/bin/cat.py	2022-12-16 13:11:34.000000000 -0800
+++ byoverbs/bin/cat.py	2023-03-02 13:59:08.000000000 -0800
@@ -19,7 +19,7 @@ options:
                         forward the input formatted as a Python String or Bytes Literal

 quirks:
-  goes well with:  find.py
+  goes well with Cat N Expand, NL Expand, Paste Seq Expand
   classic Cat rudely hangs with no prompt, when given no Parms with no Stdin
   classic Cat rudely dumps raw Bytes, like 'less -r', unlike 'less -R' and 'less'
   Mac 'cat -tv' misprints same blank for $'\xC2\xA0' NoBreakSpace as $'\x20' Space
@@ -38,6 +38,10 @@ examples:
   cat -  # hangs till you provide input
   cat.py -  # prompts for input

+  ... |cat -n |expand
+  ... |nl -v1 |expand
+  paste <(seq 1 9999) <(...) |expand
+
   echo $'some Spaces "\x20\xC2\xA0" more equal than others' |cat -tv  # fails at Mac

   echo $'some Spaces "\x20\xC2\xA0" more equal than others' |pbcopy
@@ -63,8 +67,8 @@ examples:
 import byotools as byo


-byo.exit(__name__)
+byo.sys_exit_if()

"""


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/cat.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
