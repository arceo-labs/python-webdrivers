# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools.command.build_py import build_py

import os
import zipfile

try:
    from io import BytesIO
    from urllib.request import urlopen, URLError
except ImportError:
    from StringIO import StringIO as BytesIO
    from urllib2 import urlopen, URLError

__author__ = 'Russell Snyder <ru.snyder@gmail.com>'

with open('README.md') as readme_file:
    long_description = readme_file.read()

setup(
    name="python-webdrivers",
    version="0.1.0",
    author="Russell Snyder",
    author_email="ru.snyder@gmail.com",
    description="Easy download and use of browser drivers",
    license="MIT",
    keywords="chromedriver chrome browser selenium",
    url="https://github.com/arceo-labs/python-webdrivers",
    packages=["webdrivers"],
    install_requires=[
        'cssselect',
        'lxml',
        'selenium'
    ],
    long_description_content_type="text/markdown",
    long_description=long_description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Installation/Setup",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
    ]
)
