SHELL:=/bin/bash

PROJECT := cloudsplaining
PROJECT_UNDERSCORE := cloudsplaining

virtualenv:
	python3 -m venv ./venv && source venv/bin/activate

setup-env: virtualenv
	python3 -m pip install -r requirements.txt

setup-dev: setup-env
	python3 -m pip install -r requirements-dev.txt

# Create the documentation files and open them locally
build-docs: clean virtualenv
	mkdocs build

# Serve the docs locally as you edit them
serve-docs: clean virtualenv
	mkdocs serve --dev-addr "127.0.0.1:8001"

# Build the cloudsplaining package from the current directory contents for use with PyPi
build: setup-env clean
	python3 -m pip install --upgrade setuptools wheel
	python3 -m setup -q sdist bdist_wheel

# Install the package locally
install: build
	python3 -m pip install -q ./dist/${PROJECT}*.tar.gz
	${PROJECT} --help

# Uninstall the package
uninstall:
	python3 -m pip uninstall ${PROJECT} -y
	python3 -m pip uninstall -r requirements.txt -y
	python3 -m pip uninstall -r requirements-dev.txt -y
	python3 -m pip freeze | xargs python3 -m pip uninstall -y

# Clean the directory of extra python files
clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '*.egg-link' -delete
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +

# Run unit tests
test: setup-dev
	python3 -m coverage run -m pytest -v

# Run python security tests
security-test: setup-dev
	bandit -r ./${PROJECT_UNDERSCORE}/

# Auto format your python files
fmt: setup-dev
	black ${PROJECT_UNDERSCORE}/

# Run Pylint to lint your code
lint: setup-dev
	pylint ${PROJECT_UNDERSCORE}/

# Publish to PyPi
publish: build
	python3 -m pip install --upgrade twine
	python3 -m twine upload dist/*
	python3 -m pip install ${PROJECT}

# count lines of code
count-loc:
	echo "If you don't have tokei installed, you can install it with 'brew install tokei'"
	echo "Website: https://github.com/XAMPPRocky/tokei#installation'"
	tokei ./* --exclude --exclude '**/*.html' --exclude '**/*.json' --exclude "docs/*" --exclude "examples/*" --exclude "test/*"

# Generate the example report
generate-report:
	python3 ./utils/generate_example_iam_data.py
	python3 ./utils/generate_example_report.py

# Install javascript packages
install-js:
	npm install

# Install javascript packages, but only the ones needed for the final report (not dev ones)
install-js-production:
	rm -rf node_modules/
	npm install --production

# Generate the updated Javascript bundle
build-js: setup-env install-js-production
	python3 ./utils/generate_example_iam_data.py
	npm run build

# Run Javascript unit tests
.PHONY: test-js
test-js: install-js
	npm test

# Serve the example Javascript report locally for development
.PHONY: serve-js
serve-js: install-js-production
	npm run serve
