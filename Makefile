# byoverbs/Makefile


#
# Run from the Sh Command Line
#


# Show these examples and exit

default:
	@echo
	@echo 'make  # shows these examples and exits'
	@echo 'make help  # shows more help lines and exits'
	@echo 'make push  # restyles & tests the source, then tells me to push it'
	@echo
	@echo 'open https://twitter.com/intent/tweet?text=.@PELaVarre'
	@echo


# Show these help lines and exit

help:
	@echo
	@echo
	@echo 'usage: make [help|push]'
	@echo
	@echo 'work to add Code into GitHub ByoVerbs'
	@echo
	@echo 'examples:'
	@echo
	@echo '  make  # shows examples and exits'
	@echo '  make help  # shows these help lines and exits'
	@echo '  make push  # restyles & tests the source, then tells me to push it'
	@echo
	@echo '  open https://twitter.com/intent/tweet?text=.@PELaVarre'
	@echo
	@echo


# Restyle & test the source, then tell me to push it

push: black flake8 shellcheck selftest
	rm -fr bin/__pycache__/
	rm -fr tmp/
	:
	git log --oneline --no-decorate -1
	git status --short --ignored
	git describe --always --dirty
	:
	: did you mean:  git push
	: press ⌃D to execute, or ⌃C to quit
	cat - >/dev/null
	git push
	:


# Restyle the commas, quotes, spaces, and tabs of the Python Source Files

black:
	~/.pyvenvs/black/bin/black ../byoverbs


# Lint the Python Source Files, quickly and meaningfully

flake8:
	~/.pyvenvs/flake8/bin/flake8 \
		--max-line-length=999 --max-complexity 10 --ignore=E203,W503 ../byoverbs
	# --ignore=E203  # Black '[ : ]' rules over E203 whitespace before ':'
	# --ignore=W503  # 2017 Pep 8 and Black over W503 line break before bin op


# Lint the Bash Source Files, quickly

shellcheck:
	mkdir -p tmp/
	demos/shellcheck.bash


# Test the source

selftest:
	:


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/Makefile
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
