r"""
usage: ssh.py [--h] [-t] [-f CONFIG] ...

shell out to a host

options:
  --help      show this help message and exit
  -t          forward control of the local terminal (-tt for more force)
  -F CONFIG   choose a file of options (default '~/.ssh/config')
  -o COMMAND  try things that could be saved into your '~/.ssh/config'

quirks:
  goes well with:  ssh-add.py
  classic Ssh rudely exits via a Code 255 Usage Error, when given no Parms

examples:

  ls -d -alF ~/.ssh/ && ls -alF ~/.ssh/config

  ssh.py  # show these examples and exit
  ssh.py --h  # show this help message and exit
  ssh.py --  # todo: run as you like it

  ssh -F /dev/null $USER@localhost
  ssh -t localhost "cd $PWD && bash -i"

  ssh-add -l  # work to shrug off differences between your '~/.ssh/config' and mine
  ssh -A -t -F /dev/null \
    -o 'UserKnownHostsFile /dev/null' \
    -o 'StrictHostKeyChecking no' \
    -o 'LogLevel QUIET' "$USER@localhost"
"""
# loop to retry, only while exit codes nonzero


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/ssh.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
