import setuptools
import os
import re

HERE = os.path.dirname(__file__)
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')
TESTS_REQUIRE = [
    'coverage',
    'nose',
    'pytest'
]


def get_version():
    init = open(os.path.join(HERE, 'cloudsplaining/bin/', 'cloudsplaining')).read()
    return VERSION_RE.search(init).group(1)


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cloudsplaining",
    include_package_data=True,
    version=get_version(),
    author="Kinnaird McQuade",
    author_email="kinnairdm@gmail.com",
    description="Explain AWS IAM policies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kmcquade/cloudsplaining",
    packages=setuptools.find_packages(exclude=['test*', 'tmp*']),
    tests_require=TESTS_REQUIRE,
    install_requires=[
        'policy_sentry',
        'click',
        'click_log',
        'schema',
        'boto3',
        'botocore',
        'markdown',
        'jinja2',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords='aws iam roles policy policies privileges security',
    python_requires='>=3.6',
    scripts=['cloudsplaining/bin/cloudsplaining'],
)
