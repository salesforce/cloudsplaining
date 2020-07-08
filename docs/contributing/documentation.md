# Contributing to Documentation

## ReadTheDocs

If you're looking to help document Cloudsplaining, your first step is to
get set up with Mkdocs, our documentation tool. First you will want to
make sure you have a few things on your local system:

-   python-dev (if you're on OS X, you already have this)
-   pip

Once you've got all that, the rest is simple:

```bash
# If you have a fork, you'll want to clone it instead
git clone git@github.com:salesforce/cloudsplaining.git

# Set up the virtual environment
python3 -m venv ./venv && source venv/bin/activate
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt

# Create the HTML files
invoke docs.build-docs
invoke docs.serve-docs

# The above will open the built documentation in your browser
```

## Report Guidance documents

The report contents are stored separately in the directory `cloudsplaining/output/templates/guidance`. You can edit them there and submit a pull request.
