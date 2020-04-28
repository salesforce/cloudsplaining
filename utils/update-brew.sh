#!/usr/bin/env bash
set -x
pipenv install --dev
rm -rf ./dist ./build
pipenv run invoke build.build-package
pipenv uninstall --all
pipenv run pip install dist/cloudsplaining-*.tar.gz -U
pipenv run pip install homebrew-pypi-poet
pipenv run poet -f cloudsplaining > HomebrewFormula/cloudsplaining.rb
