# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import re
from pathlib import Path

import setuptools

HERE = Path(__file__).parent
VERSION_RE = re.compile(r"""__version__ = ['"]([0-9.]+)['"]""")
TESTS_REQUIRE = ["coverage", "nose", "pytest"]
REQUIRED_PACKAGES = [
    "boto3",
    "botocore",
    "cached-property",
    "click",
    "click_option_group",
    "jinja2",
    "markdown",
    "policy_sentry>=0.14.0,<0.15",
    "pyyaml",
    "schema",
]
PROJECT_URLS = {
    "Documentation": "https://policy-sentry.readthedocs.io/",
    "Example Report": "https://opensource.salesforce.com/cloudsplaining",
    "Code": "https://github.com/salesforce/cloudsplaining/",
    "Twitter": "https://twitter.com/kmcquade3",
    "Red Team Report": "https://opensource.salesforce.com/policy_sentry",
}


def get_version() -> str:
    init = (HERE / "cloudsplaining/bin/version.py").read_text()
    return VERSION_RE.search(init).group(1)


def get_description() -> str:
    return (HERE / "README.md").read_text()


setuptools.setup(
    name="cloudsplaining",
    include_package_data=True,
    version=get_version(),
    author="Kinnaird McQuade",
    author_email="kinnairdm@gmail.com",
    description="AWS IAM Security Assessment tool that identifies violations of least privilege and generates a risk-prioritized HTML report.",
    long_description=get_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/salesforce/cloudsplaining",
    packages=setuptools.find_packages(exclude=["test*", "tmp*"]),
    tests_require=TESTS_REQUIRE,
    install_requires=REQUIRED_PACKAGES,
    project_urls=PROJECT_URLS,
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": "cloudsplaining=cloudsplaining.bin.cli:main"},
    zip_safe=True,
    keywords="aws iam roles policy policies privileges security",
    python_requires=">=3.9",
)
