if !:; then

    visit

        https://shell.cloud.google.com/?show=terminal

    give it this one line, and press Return

        curl -Ss https://github.com/pelavarre/byoverbs/main/pwnme/tictactoe.bash |bash

fi

rm -fr byoverbs/  # uninstall
git clone https://github.com/pelavarre/byoverbs.git  # reinstall
ls -1 byoverbs/pwnme/*  # list the games

byoverbs/demos/tictactoe.py --  # start playing Tic-Tac-Toe in particular


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/pwnme/tictactoe.bash
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
