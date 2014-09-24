# (C)2012 Lukas Czerner <lczerner@loguj.cz>

all:
	rm -f monorail/ai.c monorail/ai.so
	rm -rf monorail/data
	@python2 setup.py build_ext --inplace
	ln -s $(CURDIR)/data/800x600/ monorail/data

help:
	@echo "Usage: make <target>"
	@echo
	@echo "Available targets are:"
	@echo " help                    show this text"
	@echo " clean                   remove python bytecode and temp files"
	@echo " git-clean               remove all files outside git tree"
	@echo " install                 install program on current system"
	@echo " source                  create source tarball"
	@echo " rebuild-all             rebuild everything including all assets"

clean:
	@python2 setup.py clean
	rm -f MANIFEST
	rm -f monorail/ai.c monorail/ai.so
	rm -rf monorail/data
	rm -rf assets/tmp
	find . -\( -name "*.pyc" -o -name '*.pyo' -o -name "*~" -\) -delete

git-clean:
	git clean -f

install:
	@python2 setup.py install

source: clean
	@python2 setup.py sdist

rebuild-all: clean
	@python2 setup.py build_ext --inplace
	@python2 build.py
