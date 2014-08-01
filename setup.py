#!/usr/bin/env python

import pyconfd

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

requires = []

packages = [
    "pyconfd",
]

setup(
    name="pyconfd",
    version=pyconfd.__version__,
    description="Auto update config files from consul or etcd.",
    author="Bryan Bishop",
    author_email="kanzure@gmail.com",
    url="https://github.com/kanzure/pyconfd",
    install_requires=requires,
    packages=packages,
    license="BSD",
    classifiers=(
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
    ),
)
