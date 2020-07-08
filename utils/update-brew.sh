#!/usr/bin/env bash
set -x
python3 -m venv ./venv && source venv/bin/activate
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt
invoke build.build-package
pip uninstall -r requirements.txt -y
pip uninstall -r requirements-dev.txt -y
pip install homebrew-pypi-poet
pip install cloudsplaining -U
poet -f cloudsplaining > HomebrewFormula/cloudsplaining.rb
