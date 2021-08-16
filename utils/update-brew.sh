#!/usr/bin/env bash
set -x
python3 -m venv ./venv && source venv/bin/activate

pip install homebrew-pypi-poet
pip install cloudsplaining -U


pip uninstall -r requirements.txt -y
pip uninstall -r requirements-dev.txt -y
pip install homebrew-pypi-poet
pip install cloudsplaining -U
poet -f cloudsplaining > HomebrewFormula/cloudsplaining.rb
