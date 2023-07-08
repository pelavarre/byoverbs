# byoverbs/Makefile


#
# Run from the Sh Command Line
#


# Show examples and exit
#
#   cat Makefile |expand |grep '^[^ :]*:' |grep -v '^[.]PHONY:' |cut -d: -f1
#   # don't help with:  default, black, flake8, shellcheck, selftest, p.py
#

default:
	@echo
	@echo 'make  # shows examples and exits'
	@echo 'make help  # shows these help lines and exits'
	@echo
	@echo 'make push  # restyles & tests the source, then tells me to push it'
	@echo "make pull  # restyles & tests the source, but doesn't say push it"
	@echo
	@echo 'make bin  # puts bin dir files under test at home bin dir'
	@echo 'make dotfiles  # updates local dotfiles dir from home dot files'
	@echo
	@echo 'open https://twitter.com/intent/tweet?text=.@PELaVarre'
	@echo


# Show help lines and exit

help:
	@echo
	@echo
	@echo 'usage: make [help|push]'
	@echo
	@echo 'work to add Code into GitHub ByoVerbs'
	@echo
	@echo 'examples:'
	@echo
	@echo '  make  # shows these examples and exits'
	@echo '  make help  # shows these help lines and exits'
	@echo
	@echo '  make push  # restyles & tests the source, then tells me to push it'
	@echo "  make pull  # restyles & tests the source, but doesn't say push it"
	@echo
	@echo '  make bin  # puts bin dir files under test at home bin dir'
	@echo '  make dotfiles  # updates local dotfiles dir from home dot files'
	@echo
	@echo '  open https://twitter.com/intent/tweet?text=.@PELaVarre'
	@echo
	@echo


# Restyle & test the source, then tell me to push it

push: pull
	: did you mean:  git push
	: press ⌃D to execute, or ⌃C to quit
	cat - >/dev/null
	git push
	exit 0
	:

pull: black flake8 shellcheck selftest
	:
	demos/last2lines.py ./ bin/ demos/
	:
	rm -fr bin/__pycache__/byotools.cpython-*.pyc
	rm -fr tmp/
	:
	git log --oneline --no-decorate -1
	git status --short --ignored
	git describe --always --dirty
	:
	exit 0


#
# Patch the source
#


# Restyle the commas, quotes, spaces, and tabs of the Python Source Files

black:
	~/.pyvenvs/black/bin/black ../byoverbs


# Lint the Python Source Files, quickly and meaningfully

flake8:
	source ~/.pyvenvs/flake8/bin/activate && pip freeze |grep '^flake8-import-order==' >/dev/null
	~/.pyvenvs/flake8/bin/flake8 \
		--max-line-length=999 --max-complexity 10 --ignore=E203,W503 ../byoverbs
# --ignore=E203  # Black '[ : ]' rules over E203 whitespace before ':'
# --ignore=W503  # 2017 Pep 8 and Black over W503 line break before bin op


# Lint the Bash Source Files, quickly

shellcheck:
	mkdir -p tmp/
	bin/shellcheck.bash
	exit 0


#
# Test the source
#


selftest:
	:


#
# Create a small Py File
#

p.py:
	printf 'def main():\n    print("Hello, World!")\n\n\nmain()\n' >p.py


# Put Bin Dir Files under test at Home Bin Dir

.PHONY: bin  # make input:  ls -d ./bin
bin:
	rm -fr bin/__pycache__/
	cp -pR bin/* ~/bin/.
	bash -c 'diff -bpru <(ls -1 ~/bin |grep -v ^__pycache__$$) <(ls -1 bin)'
	exit 0


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
	exit 0


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/Makefile
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
