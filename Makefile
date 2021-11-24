.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 kafka_connect_api tests

test: ## run tests quickly with the default Python
	pytest

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source kafka_connect_api -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/kafka_connect_api.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ kafka_connect_api
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	twine check dist/*
	poetry publish --build

release-test: dist ## package and upload a release
	twine check dist/* || echo Failed to validate release
	poetry config repositories.pypitest https://test.pypi.org/legacy/
	poetry publish -r pypitest --build

dist: clean ## builds source and wheel package
	poetry build
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	pip install . --use-pep517 --use-feature=in-tree-build


conform	: ## Conform to a standard of coding syntax
	isort --profile black kafka_connect_api
	black kafka_connect_api tests
	find kafka_connect_api -name "*.json" -type f  -exec sed -i '1s/^\xEF\xBB\xBF//' {} +

python39	:
			docker run -u $(shell bash -c 'id -u'):$(shell bash -c 'id -u') \
			--rm -v $(PWD):/opt/build --workdir /opt --entrypoint /bin/bash \
			public.ecr.aws/compose-x/python:3.9 \
			-c "pip install --no-cache-dir /opt/build/dist/*.whl -t /opt/build/layer/lib/python/python3.9/site-packages/"

python38	:
			docker run -u $(shell bash -c 'id -u'):$(shell bash -c 'id -u') \
			--rm -v $(PWD):/opt/build --workdir /opt/build --entrypoint /bin/bash \
			public.ecr.aws/compose-x/python:3.8 \
			-c "pip install --no-cache-dir /opt/build/dist/*.whl -t /opt/build/layer/lib/python/python3.8/site-packages/"


layers		: dist
			test -d layer && rm -rf layer || mkdir layer
			$(MAKE) python38
			$(MAKE) python39
			cleanpy -af --include-testing layer/lib/python/python3.8/site-packages/
			cleanpy -af --include-testing layer/lib/python/python3.9/site-packages/

package		: layers
			cd layer; mkdir python; mv * python ; zip -r9 ../layer.zip *
			$(MAKE) clean
