# byoverbs/Makefile


#
# Help ship our Code early & often
#


# Show examples and exit
#
# Do help with:  help, pips, push, smoke, bin, dotfiles, slow
# Don't help with:  default, h, black, flake8, mypy, shellcheck, selftest, p.py
#
# Do consider helping with all of
#
#	cat Makefile |expand |grep '^[^ :]*:' |grep -v '^[.]PHONY:' |cut -d: -f1 \
#       |grep -v -e^{help,pips,push,smoke,bin,dotfiles,slow}$
#

default:
	@echo
	@echo 'make  # shows examples and exits'
	@echo 'make help  # shows these help lines and exits'
	@echo
	@echo 'make pips  # rewrites ~/.pyvenvs/pips/'
	@echo 'make push  # restyles & tests the source, then tells you to push it'
	@echo "make smoke  # restyles & tests the source, but doesn't say push it"
	@echo
	@echo 'make bin  # puts bin dir files under test at home bin dir'
	@echo 'make dotfiles  # updates local dotfiles dir from home dot files'
	@echo "make slow  # run the expensive self-test's"
	@echo
	@echo 'open https://twitter.com/intent/tweet?text=.@PELaVarre'
	@echo


# Show help lines and exit

h: help
	@

help:
	@echo
	@echo
	@echo 'usage: make [help|pips|push|smoke|bin|dotfiles|slow]'
	@echo
	@echo 'work to add Code into GitHub ByoVerbs'
	@echo
	@echo 'examples:'
	@echo
	@echo '  make  # shows these examples and exits'
	@echo '  make help  # shows these help lines and exits'
	@echo
	@echo '  make pips  # rewrites ~/.pyvenvs/pips/'
	@echo '  make push  # restyles & tests the source, then tells you to push it'
	@echo "  make smoke  # restyles & tests the source, but doesn't say push it"
	@echo
	@echo '  make bin  # puts bin dir files under test at home bin dir'
	@echo '  make dotfiles  # updates local dotfiles dir from home dot files'
	@echo "  make slow  # run the expensive self-test's"
	@echo
	@echo '  open https://twitter.com/intent/tweet?text=.@PELaVarre'
	@echo
	@echo


# Add on to Python

pips: ~/.pyvenvs/pips/
	source ~/.pyvenvs/pips/bin/activate && pip install --upgrade black
	source ~/.pyvenvs/pips/bin/activate && pip install --upgrade flake8
	source ~/.pyvenvs/pips/bin/activate && pip install --upgrade flake8-import-order
	source ~/.pyvenvs/pips/bin/activate && pip install --upgrade mypy

~/.pyvenvs/pips/:
	mkdir -p  ~/.pyvenvs
	rm -fr ~/.pyvenvs/pips/
	(cd ~/.pyvenvs/ && python3 -m venv pips --prompt PIPS)


# Restyle & test the source, then tell me to push it

push: smoke
	: did you mean:  git push
	: press ⌃D to execute, or ⌃C to quit
	cat - >/dev/null
	ssh-add -l ||:
	git push
	:

smoke: black flake8 mypy shellcheck selftest
	:
	demos/last2lines.py ./ bin/ demos/
	:
	rm -fr .mypy_cache/
	rm -fr __pycache__/ bin/__pycache__/ demos/__pycache__/
	rm -fr tmp/
	:
	git log --oneline --no-decorate -1
	git status --short --ignored
	git describe --always --dirty
	:

# todo: no 'last2lines' cover for:  git grep -l 'posted as' |grep -v .py$


#
# Patch the source
#


# Restyle the commas, quotes, spaces, and tabs of the Python Source Files

black:
	~/.pyvenvs/black/bin/black --line-length=101 ../byoverbs
	:


# Lint the Python Source Files, quickly and meaningfully

flake8:
	source ~/.pyvenvs/flake8/bin/activate && \
		pip freeze |grep '^flake8.import.order==' >/dev/null
	~/.pyvenvs/flake8/bin/flake8 \
		--max-line-length=999 --max-complexity 15 --ignore=E203,W503 \
		../byoverbs 2>&1 \
		|cat -
	:

# --max-line-length=999  # Black max line lengths over Flake8 max line lengths
# --max-complexity 15  # limit how much McCabe Cyclomatic Complexity we accept
# --ignore=E203  # Black '[ : ]' rules over E203 whitespace before ':'
# --ignore=W503  # 2017 Pep 8 and Black over W503 line break before bin op


# Lint the Python Data Types, quickly and meaningfully

mypy:
	grep -nR '^ *def ' bin/*.py demos/l*.py |grep -v ') -> ' || :
	# git diff --color-moved HEAD~1 |grep '[^f]".*[{]..*[}].*"' || :
	mv -i __init__.py ../__init__.py~
	~/.pyvenvs/mypy/bin/mypy bin || (mv -i ../__init__.py~ __init__.py && exit 1)
	mv -i ../__init__.py~ __init__.py
	# todo: more widely adopt MyPy Code-Review of Python Data-Types
	:


# Lint the Bash Source Files, quickly

shellcheck:
	mkdir -p tmp/
	bin/shellcheck.bash  # not:  bin/shellcheck.bash -o all --exclude=...
	:


#
# Test the source
#


selftest:
	:
	bin/pq.py >/dev/null
	python3 demos/byoverbs.py -- >/dev/null
	:

slow:
	:
	: ./demos/pq-make-txt.bash ... >demos/pq.txt ...
	date && time ./demos/pq-make-txt.bash </dev/null >demos/pq.txt 2>&1
	: consider accept 'make slow' via:  git add -p
	: consider undo 'make slow' via:  git checkout HEAD demos/pq.txt
	git diff demos/pq.txt
	:


#
# Create a small Py File
#

p.py:
	printf 'def main():\n    print("Hello, World!")\n\n\nmain()\n' >p.py
	:


# Put Bin Dir Files under test at Home Bin Dir

.PHONY: bin  # make input:  ls -d ./bin
bin:
	rm -fr bin/__pycache__/
	cp -pR bin/* ~/bin/.
	bash -c 'diff -bpru <(ls -1 ~/bin |grep -v ^__pycache__$$) <(ls -1 bin)'
	:


# Publish many $HOME DotFiles, even the Bash less tested at Mac than the Zsh

.PHONY: dotfiles  # make input:  ls -d ./dotfiles
dotfiles:
	cp -p ~/.bash_profile dotfiles/dot.bash_profile
	cp -p ~/.bashrc dotfiles/dot.bashrc
	cp -p ~/.emacs dotfiles/dot.emacs
	# cp -p ~/.gitconfig dotfiles/dot.gitconfig  # nope, '[user]' differs
	cp -p ~/.hushlogin dotfiles/dot.hushlogin
	cp -p ~/.vimrc dotfiles/dot.vimrc
	cp -p ~/.zprofile dotfiles/dot.zprofile
	cp -p ~/.zshrc dotfiles/dot.zshrc
	git diff || :
	# also consider:  cp -p ~/.gitconfig dotfiles/dot.gitconfig
	:


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/Makefile
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
