default:
    @just --list

[group('docs')]
build-docs:
    mkdocs build

[group('js')]
build-js: clean-js install-js
    uv run ./utils/generate_example_iam_data.py
    npm run build

[group('package')]
build-package: clean
    uv build

[group('package')]
clean:
    rm -rf dist/
    rm -rf *.egg-info

[group('js')]
clean-js:
    rm -rf node_modules/
    npm cache clear --force

[group('js')]
generate-report:
    uv run ./utils/generate_example_iam_data.py
    uv run ./utils/generate_example_report.py

[group('js')]
install-js:
    npm ci

[group('docs')]
serve-docs:
    mkdocs serve --dev-addr "127.0.0.1:8001"

[group('js')]
serve-js: install-js
    npm run serve

[group('js')]
test-js: install-js
    npm test

[group('test')]
type-check:
    ty check

[group('test')]
unit-tests:
    coverage run -m pytest -v
    coverage report -m
