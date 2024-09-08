# ~/.ssh/zprofile


# Bind ⌃X ⌃E without ⌃X E

autoload -U edit-command-line
zle -N edit-command-line
bindkey '^x^e' edit-command-line

EDITOR='pq xeditline'  # yes assigned, but Not-export'ed


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/dotfiles/dot.bash_profile
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
