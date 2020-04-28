# Contributing to Documentation

## ReadTheDocs

You can contribute to the User Guide and ReadTheDocs documentation itself by editing the
Markdown files in the `docs/` folder.

To see what it looks like, enter your Pipenv and run the PyInvoke command to build the docs:

```bash
pipenv shell
pipenv install --dev
invoke docs.build-docs
```

Then open your browser to [http://127.0.0.1:8000](http://127.0.0.1:8000) to view the documentation.

## Report Guidance documents

The report contents are stored separately in the directory `cloudsplaining/output/templates/guidance`. You can edit them there and submit a pull request.
