#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

requires = ["gevent", "Jinja2"]

packages = [
    "pyconfd",
]

setup(
    name="pyconfd",
    version="0.0.7",
    description="Auto update config files from consul or etcd.",
    author="Bryan Bishop",
    author_email="kanzure@gmail.com",
    license="BSD",
    url="https://github.com/kanzure/pyconfd",
    install_requires=requires,
    packages=packages,
    entry_points={
        "console_scripts": [
            "pyconfd = pyconfd.core:main",
        ],
    },
    classifiers=(
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
    ),
)
