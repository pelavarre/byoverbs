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
  classic Ssh -i PrivateKey doesn't help you log in, if you've loaded too many Keys
  classic Ssh rudely exits nonzero, despite printing Help, when give no Sh Args

examples:

  ls -d -alF ~/.ssh/ && ls -alF ~/.ssh/config

  ssh.py  # show these examples and exit
  ssh.py --h  # show this help message and exit
  ssh.py --  # todo: run as you like it

  ssh -F /dev/null $USER@localhost  # log in without interference from '~/.ssh/config'
  ssh -t localhost "cd $PWD && bash -i"  # log in and do setup, then chat

  ssh-add -l  # work to shrug off differences between your '~/.ssh/config' and mine
  ssh-add -L |ssh-keygen -L -f - |grep Valid  # guess when Keys expire
  ssh-add -D && ssh-add -l  # exit 1 via forgetting the loaded Keys
  SSH_AUTH_SOCK= ssh-add -l  # exit 2 via hiding the loaded Keys

  ssh -A -t -F /dev/null \
    -o 'UserKnownHostsFile /dev/null' \
    -o 'StrictHostKeyChecking no' \
    -o 'LogLevel QUIET' "$USER@localhost"

  : # some people upvote:  -o IdentityFile=/dev/null
"""
# loop to retry, only while exit codes nonzero


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/ssh.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
