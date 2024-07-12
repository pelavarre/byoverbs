#!/usr/bin/env python3

"""
For copying a Csv into Google Sheets, you might most like

a) http://sheets.new/

b) File > Import > Upload > Browse > (choose file) > Import Data
... and wait for the Rows of Columns of Blank Cells to disappear ...

c) Format > Convert to Table
So long as the first row of your Csv gave a Column Name to each Column,
these 3 steps and done, it comes out well

d) Delete the Rows you don't want, from the bottom of the Table

P.S. These Cells copy out from G Sheet as Tsv, and
they paste back in well if you choose ⇧⌘V to ask for Paste Special > Values Only

"""

import byotools as byo


byo.sys_exit()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/gsheets.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
