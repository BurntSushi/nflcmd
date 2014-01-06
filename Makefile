REMOTE=Geils:~/www/burntsushi.net/public_html/stuff/nflcmd/

all:
	@echo "Specify a target."

pypi: docs longdesc.rst
	sudo python2 setup.py register sdist bdist_wininst upload

docs:
	pdoc --html --html-dir ./doc --overwrite ./nflcmd

longdesc.rst: nflcmd/__init__.py docstring
	pandoc -f markdown -t rst -o longdesc.rst docstring
	rm -f docstring

docstring: nflcmd/__init__.py
	./scripts/extract-docstring > docstring

dev-install:
	[[ -n "$$VIRTUAL_ENV" ]] || exit
	rm -rf ./dist
	python setup.py sdist
	pip install -U dist/*.tar.gz

pep8:
	pep8-python2 nflcmd/*.py nflcmd/cmds/*.py
	pep8-python2 scripts/nfl{rank,stats}

push:
	git push origin master
	git push github master
