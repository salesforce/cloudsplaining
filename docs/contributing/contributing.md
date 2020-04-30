# Contributing

We use Pipenv for package management. PyInvoke is used for storing common commands.

## Pipenv

```bash
pipenv --python 3.7  # create the environment
pipenv shell         # start the environment
pipenv install       # install both development and production dependencies
```


## Invoke
To run and develop Policy Sentry without having to install from PyPi, you can use Invoke.

```bash
# List available tasks
invoke -l

# that will show the following options:
Available tasks:

  build.build-package         Build the cloudsplaining package from the current
                              directory contents for use with PyPi
  build.install-package       Install the cloudsplaining package built from the
                              current directory contents (not PyPi)
  build.uninstall-package     Uninstall the cloudsplaining package
  build.upload-prod           Upload the package to the PyPi production server
                              (requires credentials)
  build.upload-test           Upload the package to the TestPyPi server
                              (requires credentials)
  docs.build-docs             Create the documentation files and open them
                              locally
  integration.expand-policy   Integration testing: tests the expand-policy
                              command
  test.format                 Auto format code with Python `black`
  test.lint                   Lint the code
  test.security               Runs `bandit` and `safety check`
  unit.nose                   Unit testing: Runs unit tests using `nosetests`
  unit.pytest                 Unit testing: Runs unit tests using `pytest`

# To run them, specify `invoke` plus the options:
  invoke build.build-package
  invoke docs.build-docs
  invoke test.lint
  invoke unit.nose
  invoke unit.pytest
  invoke test.security

```
