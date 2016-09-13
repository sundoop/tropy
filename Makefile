# You can set these variables from the command line.
PEP8_TARGET   = .
NOSE_TARGET   =

# Internal variables
null  :=
space := $(null) #
comma := ,

# Executables
PIP = pip
PEP8 = pep8
NOSE = nosetests
PYTHON = python

# PEP8 variables
# Exclusion directories should be set in pep8.conf instead of here if possible
PEP8_OPTS = --config=./pep8.conf
PEP8_ALL_OPTS = $(PEP8_TARGET) $(PEP8_OPTS)

# Nose and test variables
NOSE_PACKAGES_TO_COVER = tropy
NOSE_EXCLUDE_DIRS =
COVERAGE_OUTPUT_FILES = .coverage coverage.xml nosetests.xml
NOSE_OPTIONS += --no-byte-compile --no-path-adjustment --verbose
NOSE_COVERAGE_OPTIONS = --cover-branches --cover-erase --cover-tests --with-coverage

ifdef NOSE_EXCLUDE_DIRS
NOSE_OPTIONS += $(patsubst %,--exclude-dir=%,$(strip $(NOSE_EXCLUDE_DIRS)))
endif
ifdef NOSE_PACKAGES_TO_COVER
NOSE_COVERAGE_OPTIONS += --cover-package=$(subst $(space),$(comma),$(strip $(NOSE_PACKAGES_TO_COVER)))
endif

.PHONY: help clean tests coverage coveragehtml

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  pep8            to run PEP8, you can set PEP8_TARGET=<file or dir>"
	@echo "  tests           to run all tests, you can set NOSE_TARGET=<file, dir, or python module>"
	@echo "  pip             to install Python dependencies"

clean:
	find . -name '*.pyc' -delete
	$(RM) $(COVERAGE_OUTPUT_FILES)
	rm -rf cover

coverage:
	$(NOSE) $(NOSE_OPTIONS) $(NOSE_COVERAGE_OPTIONS) $(NOSE_TARGET)

coveragehtml:
	$(NOSE) $(NOSE_OPTIONS) $(NOSE_COVERAGE_OPTIONS) $(NOSE_TARGET) --cover-html

tests:
	$(NOSE) $(NOSE_OPTIONS) $(NOSE_TARGET)

pep8:
	$(PEP8) $(PEP8_ALL_OPTS)

pip: dev-requirements.txt requirements.txt
	pip install $(PIP_INSTALL_OPTS) -r dev-requirements.txt
