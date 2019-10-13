import sys
from setuptools import setup, find_packages
from bata8.version import version

setup(
    name = 'bata8',
    version = version,
    description = 'aws resource viewer',
    install_requires = [
        "boto3 >= 1.9.210",
    ],
    packages = find_packages(),
    python_requires = '>=3.6',
    entry_points = {
        "console_scripts": [
            "bata8 = bata8.main:main",
        ],
    },
)

