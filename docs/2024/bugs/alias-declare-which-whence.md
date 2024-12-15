# bugs/alias-declare-which-whence.md

Classic Sh hides away from you how wildly it will misread your first Input Word.
Many separate Apps work together to guess what you mean.


## Glitches

Try a probe like

    which -a which

and you may see

    which: shell built-in command
    /usr/bin/which
    /bin/which

You're working with a fragmentation that can hide away
the meaning of your first Input Word, the main imperative Verb you spoke,
in many different places, nearly always in these five places

    alias -p  # Bash
    alias  # Zsh
    declare -f
    which -a
    whence -a  # Zsh

The definitions that come to you, so very hidden away, they often vary,
as you choose between many many ways of launching your Sh, such as

    bash
    bash -l  # like login, to run your ~/.bash_profile
    /usr/bin/sh  # Linux
    zsh  # macOS, but available for Linux


## Quirks

Zsh lets you give meaning to a wider range of Punctuation than Bash does, for example

    alias ./='echo dot slash'

Choosing which Punctuation to define for you,
without colliding with that same Punctuation carrying much meaning elsewhere,
can be difficult.
For example, I have gone wrong by accident or on purpose with

    :/ has much meaning inside https://example.com, inside scp localhost:/, etc

    :: has much meaning inside C++

    %% a clear meaning, without much usage, inside of C PrintF and Python % and so on

Lately I settle for defining only

    %%
    -
    ..
    ~


## Tests

    alias.py
    declare.py
    function.py
    whence.py
    which.py

    bash.py
    zsh.py

## Copied from

Posted as:  https://github.com/pelavarre/byoverbs/blob/main/bugs/alias-declare-which-whence.md
<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git
