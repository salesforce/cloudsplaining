## Python Contributions

Insert more docs on this here...

### Dependency management: Virtual environment
We use Virtualenv for package management instead of Pipenv or Poetry. Makefile is used for storing common commands.

```bash
# Set up the virtual environment
python3 -m venv ./venv && source venv/bin/activate
uv sync --frozen
```


### Makefile

* Python commands:
  
```bash
# Set up your local development environment
make setup-env

# Auto format and lint the python code with `ruff`
prek run -a

# Run unit tests with pytest
make test
```

* Javascript/UI commands
  
```bash
# Run Javascript unit tests
make test-js

# Generate the updated Javascript bundle
make build-js

# Serve the example Javascript report locally for development
make serve-js

# Generate the updated report
make generate-report
```

* Documentation commands:

```bash
# Create the documentation files locally and open them
make build-docs

# Serve the documentation files locally as you edit them
make serve-docs
```
