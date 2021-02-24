# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# Licensed under the BSD 3-Clause license.
# For full license text, see the LICENSE file in the repo root
# or https://opensource.org/licenses/BSD-3-Clause
import setuptools
import os
import re

HERE = os.path.abspath(os.path.dirname(__file__))
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')
TESTS_REQUIRE = [
    'coverage',
    'nose',
    'pytest'
]


def get_version():
    init = open(
        os.path.join(
            HERE,
            "cloudsplaining",
            "bin",
            'version.py'
        )
    ).read()
    return VERSION_RE.search(init).group(1)


def get_description():
    return open(
        os.path.join(os.path.abspath(HERE), "README.md"), encoding="utf-8"
    ).read()


setuptools.setup(
    name="cloudsplaining",
    include_package_data=True,
    version=get_version(),
    author="Kinnaird McQuade",
    author_email="kinnairdm@gmail.com",
    description="AWS IAM Security Assessment tool that identifies violations of least privilege and generates a risk-prioritized HTML report with a triage worksheet.",
    long_description=get_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/kmcquade/cloudsplaining",
    packages=setuptools.find_packages(exclude=['test*', 'tmp*']),
    tests_require=TESTS_REQUIRE,
    install_requires=[
        'policy_sentry>=0.11.3',
        'click',
        'schema',
        'boto3',
        'botocore',
        'markdown',
        'jinja2',
        'cached-property'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": "cloudsplaining=cloudsplaining.bin.cli:main"},
    zip_safe=True,
    keywords='aws iam roles policy policies privileges security',
    python_requires='>=3.6',
    # scripts=['cloudsplaining/bin/cloudsplaining'],
)
