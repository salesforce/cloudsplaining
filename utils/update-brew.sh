#!/usr/bin/env bash
set -x
pipenv uninstall --all
pipenv run pip install cloudsplaining -U
pipenv run pip install homebrew-pypi-poet
pipenv run poet -f cloudsplaining > HomebrewFormula/cloudsplaining.rb
