#!/usr/bin/env bash
set -ex
# Suppress annoying warnings
export PIPENV_VERBOSITY=-1

pip3 install pipenv
pipenv install --dev

pipenv run invoke test.lint
pipenv run invoke build.uninstall-package
pipenv run invoke build.install-package
pipenv run invoke test.security
pipenv run invoke unit.pytest

pipenv run invoke integration.version
pipenv run invoke integration.expand-policy
pipenv run invoke integration.scan

pipenv run invoke docs.build-docs
