SHELL:=/bin/bash

PROJECT := cloudsplaining

setup-env:
	uv sync --frozen

# Create the documentation files and open them locally
build-docs: clean
	mkdocs build

# Serve the docs locally as you edit them
serve-docs: clean
	mkdocs serve --dev-addr "127.0.0.1:8001"

# Build the cloudsplaining package from the current directory contents for use with PyPi
build: setup-env clean
	uv build

# Install the package locally
install: build
	uv pip install -q ./dist/${PROJECT}*.tar.gz
	${PROJECT} --help

# Uninstall the package
uninstall:
	uv pip uninstall ${PROJECT} -y

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
test: setup-env
	coverage run -m pytest -v
	coverage report -m

type-check: setup-env
	mypy

# Publish to PyPi
publish: build
	uv publish
	uv pip install ${PROJECT}

# count lines of code
count-loc:
	echo "If you don't have tokei installed, you can install it with 'brew install tokei'"
	echo "Website: https://github.com/XAMPPRocky/tokei#installation'"
	tokei ./* --exclude --exclude '**/*.html' --exclude '**/*.json' --exclude "docs/*" --exclude "examples/*" --exclude "test/*"

# Generate the example report
generate-report:
	python ./utils/generate_example_iam_data.py
	python ./utils/generate_example_report.py
# ---------------------------------------------------------------------------------------------------------------------
# JavaScript
# ---------------------------------------------------------------------------------------------------------------------
clean-js:
	rm -rf node_modules/
	npm cache clear --force

# Install javascript packages
install-js:
	npm install

# Install javascript packages, but only the ones needed for the final report (not dev ones)
install-js-production: clean-js
	npm install --production

# Generate the updated Javascript bundle
build-js: setup-env install-js-production
	python ./utils/generate_example_iam_data.py
	npm run build

# Run Javascript unit tests
.PHONY: test-js
test-js: install-js
	npm test

# Serve the example Javascript report locally for development
.PHONY: serve-js
serve-js: install-js-production
	npm run serve

# Update Homebrew file. Does not commit to Git
update-homebrew-file: uninstall
	uv pip install homebrew-pypi-poet
	uv pip install cloudsplaining -U
	git fetch origin
	latest_tag := $(git describe --tags `git rev-list --tags --max-count=1`)
	echo "latest tag: $latest_tag"
	git pull origin $latest_tag
	poet -f cloudsplaining > HomebrewFormula/cloudsplaining.rb

update-homebrew: update-homebrew-file
	git add .
	git commit -m "update brew formula" cloudsplaining/bin/version.py HomebrewFormula/cloudsplaining.rb || echo "No brew changes to commit"
	git push -u origin master
