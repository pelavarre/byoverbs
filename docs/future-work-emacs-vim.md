# docs/future-work-emacs-vim.md

Let's compare Emacs, Vim, macOS Notes, Msft VsCode, Zsh, Bash, and Pq

1 ) Vim & Pq gives you their ⎋ Meta Mode, the rest don't.
Vim launches in ⎋ Meta Mode, the rest launch in Insert Mode.
Pq launches in Replace Mode

2 ) Vim doesn't give you ⌃A ⌃B ⌃D ⌃E ⌃F ⌃K ⌃N ⌃O ⌃P ⌥← ⌥→ in Replace/ Insert Mode.
macOS & VsCode & Pq do in fact give you all of these, copied from Emacs,
although too many people never test these

3 ) Emacs inside your Shell Input Rows doesn't give you the ⎋Z "zap-to-char".
Vim gives it to you as as ⌃O D F.
You can tell Zsh to add ⎋Z,
but then Zsh wrongly doesn't ignore case and stops 1 Char too soon.
Pq gives it to your Emacs brain as ⎋Z and to your Vim Brain as ⌃Q ⌃O D F

4 ) Vim doesn't let you click to move the Terminal Cursor,
unless you think to press ⌥ Option/Alt while you click.
Vim forces you to give up ⌘C after Drag to copy Text out,
if you tell it you don't want to press ⌥ Option/Alt while you click.

5 ) Too many Vim's make you wait when you press Esc to return to Meta Mode,
and then only let ⌃C cancel this silly wait
if you do give up asking for multiple copies of your Input

6 ) Too many Zsh'es and Bash'es drop too many editing Keys,
and too many Bash'es wrongly also bold their Tab-Completion Suggestions
when you ask to bold your own Input

7 ) Only Pq

7.1 ) Gives more respect to the Keys you learned at Emacs or Vim,
without forcing you to speak only the one dialect or the other

7.2 ) Shows you exactly which Key Caps you pressed that it didn't understand

7.3 ) Nearly always holds back from shocking you with a loud audible beep

7.4 ) Runs well inside your Shell Input Rows,
or whatever part of your Terminal Screen you give it,
without needing to take over your whole Terminal Screen

7.5 ) Runs without blocking you from mouse-scroll'ing the Rows of the Terminal,
to let you look back over what you saw lately, while you edit

7.6 ) Edits Screen Rows & Columns after you print them, even though it didn't print them

7.7 ) Let's you drag & drop Folders of Folders of Files to reconfigure it

7.8 ) Lets you write Python to reconfigure it

Nobody talks clearly of these ideas.
Most Vim Docs speak of its ⎋ Meta Mode as "Normal Mode" or "Control Mode".
Striking the D F Key Caps in ⎋ Meta Mode
work differently than striking the ⇧D ⇧F Key Caps there,
and work differently from striking the ⌃D and ⌥D and ⌘D Key Caps too

## Copied from

Posted into:  https://github.com/pelavarre/byoverbs/blob/main/docs/future-work-emacs-vim.md
<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git
<br>
Sep/2024
