#!/usr/bin/env python
# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import sys
import os
import logging
from invoke import task, Collection, UnexpectedExit, Failure

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.path.pardir + "/cloudsplaining/")
    )
)

logger = logging.getLogger(__name__)
# Create the necessary collections (namespaces)
ns = Collection()

test = Collection("test")
ns.add_collection(test)

integration = Collection("integration")
ns.add_collection(integration)

unit = Collection("unit")
ns.add_collection(unit)

build = Collection("build")
ns.add_collection(build)

docs = Collection("docs")
ns.add_collection(docs)

js = Collection("js")
ns.add_collection(js)


@task
def build_docs(c):
    """Create the documentation files and open them locally"""
    c.run('mkdocs build')

@task
def serve_docs(c):
    """Create the documentation files and open them locally"""
    c.run('pip3 install -r docs/requirements.txt')
    c.run('mkdocs serve')


# Build
@task
def build_package(c):
    """Build the cloudsplaining package from the current directory contents for use with PyPi"""
    c.run("python -m pip install --upgrade setuptools wheel")
    c.run("python setup.py -q sdist bdist_wheel")


@task(pre=[build_package])
def install_package(c):
    """Install the cloudsplaining package built from the current directory contents (not PyPi)"""
    c.run("pip3 install -q dist/cloudsplaining-*.tar.gz")


@task
def uninstall_package(c):
    """Uninstall the cloudsplaining package"""
    c.run('echo "y" | pip3 uninstall cloudsplaining', pty=True)
    c.run('rm -rf dist/*', pty=True)


@task
def upload_to_pypi_test_server(c):
    """Upload the package to the TestPyPi server (requires credentials)"""
    c.run("python -m pip install --upgrade twine")
    c.run(
        "python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*"
    )
    c.run(
        "python -m pip install --index-url https://test.pypi.org/simple/ --no-deps cloudsplaining"
    )


@task
def upload_to_pypi_prod_server(c):
    """Upload the package to the PyPi production server (requires credentials)"""
    c.run("python -m pip install --upgrade twine")
    c.run("python -m twine upload dist/*")
    c.run("python -m pip install cloudsplaining")


@task(pre=[install_package])
def version_check(c):
    """Print the version"""
    try:
        c.run('./cloudsplaining/bin/cli.py --version', pty=True)
    except UnexpectedExit as u_e:
        logger.critical(f"FAIL! UnexpectedExit: {u_e}")
        sys.exit(1)
    except Failure as f_e:
        logger.critical(f"FAIL: Failure: {f_e}")
        sys.exit(1)


@task(pre=[install_package])
def expand_policy(c):
    """
    Integration testing: tests the expand-policy command
    """
    try:
        c.run(
            "./cloudsplaining/bin/cli.py expand-policy --input-file examples/policies/wildcards.json",
            pty=True,
        )
        c.run(
            "./cloudsplaining/bin/cli.py expand-policy --input-file examples/policies/explicit-actions.json",
            pty=True,
        )
    except UnexpectedExit as u_e:
        logger.critical(f"FAIL! UnexpectedExit: {u_e}")
        sys.exit(1)
    except Failure as f_e:
        logger.critical(f"FAIL: Failure: {f_e}")
        sys.exit(1)


@task(pre=[install_package])
def scan(c):
    """Integration testing: tests the scan command"""
    try:
        c.run(
            "./cloudsplaining/bin/cli.py scan --input-file examples/files/example.json --exclusions-file examples/example-exclusions.yml --skip-open-report -v debug",
            pty=True,
        )
    except UnexpectedExit as u_e:
        logger.critical(f"FAIL! UnexpectedExit: {u_e}")
        sys.exit(1)
    except Failure as f_e:
        logger.critical(f"FAIL: Failure: {f_e}")
        sys.exit(1)


# TEST - SECURITY
@task
def security_scan(c):
    """Runs `bandit` and `safety check`"""
    try:
        c.run("bandit -r cloudsplaining/")
        # c.run("safety check")
    except UnexpectedExit as u_e:
        logger.critical(f"FAIL! UnexpectedExit: {u_e}")
        sys.exit(1)
    except Failure as f_e:
        logger.critical(f"FAIL: Failure: {f_e}")
        sys.exit(1)


# TEST - format
@task
def fmt(c):
    """Auto format code with Python `black`"""
    try:
        c.run("black cloudsplaining/")
        # c.run('pylint cloudsplaining/', warn=False)
    except UnexpectedExit as u_e:
        logger.critical(f"FAIL! UnexpectedExit: {u_e}")
        sys.exit(1)
    except Failure as f_e:
        logger.critical(f"FAIL: Failure: {f_e}")
        sys.exit(1)


# TEST - LINT
@task
def run_linter(c):
    """Lint the code"""
    try:
        c.run('pylint cloudsplaining/', warn=False)
    except UnexpectedExit as u_e:
        logger.critical(f"FAIL! UnexpectedExit: {u_e}")
        sys.exit(1)
    except Failure as f_e:
        logger.critical(f"FAIL: Failure: {f_e}")
        sys.exit(1)


# UNIT TESTING
@task
def run_nosetests(c):
    """Unit testing: Runs unit tests using `nosetests`"""
    c.run('echo "Running Unit tests"')
    try:
        c.run("nosetests -v  --logging-level=CRITICAL")
    except UnexpectedExit as u_e:
        logger.critical(f"FAIL! UnexpectedExit: {u_e}")
        sys.exit(1)
    except Failure as f_e:
        logger.critical(f"FAIL: Failure: {f_e}")
        sys.exit(1)


@task
def run_pytest(c):
    """Unit testing: Runs unit tests using `pytest`"""
    c.run('echo "Running Unit tests"')
    try:
        c.run('python -m coverage run -m pytest -v')
        c.run('python -m coverage report -m')
    except UnexpectedExit as u_e:
        logger.critical(f"FAIL! UnexpectedExit: {u_e}")
        sys.exit(1)
    except Failure as f_e:
        logger.critical(f"FAIL: Failure: {f_e}")
        sys.exit(1)


@task
def npm_build(c):
    """Build the javascript bundle"""
    c.run('echo "Building the javascript bundle"')
    try:
        c.run('npm install --production')
        c.run('npm run build')
    except UnexpectedExit as u_e:
        logger.critical(f"FAIL! UnexpectedExit: {u_e}")
        sys.exit(1)
    except Failure as f_e:
        logger.critical(f"FAIL: Failure: {f_e}")
        sys.exit(1)


@task
def npm_serve(c):
    """Serve the report locally"""
    c.run('Serve the report locally"')
    try:
        c.run('npm install --production')
        c.run('npm run serve')
    except UnexpectedExit as u_e:
        logger.critical(f"FAIL! UnexpectedExit: {u_e}")
        sys.exit(1)
    except Failure as f_e:
        logger.critical(f"FAIL: Failure: {f_e}")
        sys.exit(1)


docs.add_task(build_docs, "build-docs")
docs.add_task(serve_docs, "serve-docs")

unit.add_task(run_nosetests, "nose")
unit.add_task(run_pytest, "pytest")

test.add_task(run_linter, 'lint')
test.add_task(fmt, "format")
test.add_task(security_scan, "security")

integration.add_task(version_check, "version")
integration.add_task(expand_policy, "expand-policy")
integration.add_task(scan, "scan")

build.add_task(build_package, "build-package")
build.add_task(install_package, "install-package")
build.add_task(uninstall_package, "uninstall-package")
build.add_task(upload_to_pypi_test_server, "upload-test")
build.add_task(upload_to_pypi_prod_server, "upload-prod")

# js.add_task(npm_build, "build")
# js.add_task(npm_serve, "serve")
