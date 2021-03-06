SHELL := /bin/bash

deps:
	pip install --upgrade --use-mirrors \
		    -r requirements/development.txt \
		    -r requirements/production.txt

lint:
	flake8 --exit-zero mod_genshi tests

sdist:
	python setup.py sdist

site:
	cd docs; make html

test:
	coverage run setup.py test

unittest:
	coverage run -m unittest2 discover

coverage:
	coverage report --show-missing --include="mod_genshi*"

server:
	python -m mod_genshi.server -b

clean:
	python setup.py clean --all
	find . -type f -name "*.pyc" -exec rm '{}' +
	find . -type d -name "__pycache__" -exec rmdir '{}' +
	rm -rf *.egg-info .coverage
	cd docs; make clean

docs: site
