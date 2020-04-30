#!/usr/bin/env bash
set -x
pipenv uninstall --all
yes | pipenv run pip uninstall cloudsplaining
pipenv run pip install cloudsplaining -U
pipenv run pip install homebrew-pypi-poet
pipenv run poet -f cloudsplaining > HomebrewFormula/cloudsplaining.rb
