#!/usr/bin/env bash
set -ex

pip install -r requirements.txt
pip install -r requirements-dev.txt

invoke test.lint
invoke build.uninstall-package
invoke build.install-package
invoke test.security
invoke unit.pytest

invoke integration.version
invoke integration.expand-policy
invoke integration.scan

invoke docs.build-docs
