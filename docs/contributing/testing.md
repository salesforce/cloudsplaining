# Testing

##  Local Unit Testing and Integration Testing

We highly suggest that you run all the tests before pushing a significant commit. The [just](https://github.com/casey/just) recipes below are the same ones the GitHub Actions build runs.

Run them from the root of the repository:


```bash
# Run Python unit tests
just unit-tests

# Run Javascript unit tests
just test-js

# Run Python security tests
just safety-scan
```

These execute the tests that run during the GitHub Actions build, so if they pass on your machine the CI test jobs should pass too.

