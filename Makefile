SHELL := /bin/bash

deps:
	pip install --upgrade --use-mirrors \
		    -r requirements/development.txt \
		    -r requirements/production.txt

lint:
	flake8 --exit-zero mod_genshi tests

dist:
	python setup.py sdist

site:
	cd docs; make html

test:
	coverage run setup.py test

unittest:
	coverage run -m unittest2 discover

coverage:
	coverage report --include="mod_genshi*"

clean:
	find . -type f -name "*.pyc" -exec rm '{}' +
	find . -type d -name "__pycache__" -exec rmdir '{}' +
	rm -rf *.egg-info
	cd docs; make clean

docs: site
