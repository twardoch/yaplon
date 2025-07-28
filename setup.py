#!/usr/bin/env python3

import os
import re

from setuptools import find_packages, setup

NAME = "yaplon"

readme_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")
with open(readme_file) as f:
    readme = f.read()


def get_version(*args):
    try:
        from yaplon._version import get_version
        return get_version()
    except ImportError:
        # Fallback to old method
        verstrline = open(os.path.join(NAME, "__init__.py")).read()
        VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
        mo = re.search(VSRE, verstrline, re.M)
        if mo:
            return mo.group(1)
        return "undefined"


def get_requirements(*args):
    """Get requirements from pip requirement files."""
    requirements = set()
    with open(get_absolute_path(*args)) as handle:
        for line in handle:
            # Strip comments.
            line = re.sub(r"^#.*|\s#.*", "", line)
            # Ignore empty lines
            if line and not line.isspace():
                requirements.add(re.sub(r"\s+", "", line))
    return sorted(requirements)


def get_absolute_path(*args):
    """Transform relative pathnames into absolute pathnames."""
    directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(directory, *args)


setup(
    name=NAME,
    author="Adam Twardoch",
    author_email="adam+github@twardoch.com",
    url="https://twardoch.github.io/%s/" % (NAME),
    project_urls={"Source": "https://github.com/twardoch/%s/" % (NAME)},
    version=get_version(),
    license="MIT",
    description="Python 3-based commandline converter CSV → YAML ↔ JSON ↔ PLIST ↔ XML",
    long_description=readme,
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    install_requires=get_requirements("requirements.txt"),
    extras_require={
        "dev": [
            "setuptools",
            "wheel",
            "pip",
            "twine>=3.2.0",
            "pyinstaller>=4.0",
        ]
    },
    packages=find_packages(),
    classifiers=[
        "Environment :: Console",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="yaml json plist csv xml convert cli",
    entry_points="""
        [console_scripts]
        {name}={name}.__main__:cli
        csv22json={name}.__main__:csv2json
        csv22plist={name}.__main__:csv2plist
        csv22xml={name}.__main__:csv2xml
        csv22yaml={name}.__main__:csv2yaml
        json22plist={name}.__main__:json2plist
        json22xml={name}.__main__:json2xml
        json22yaml={name}.__main__:json2yaml
        plist22json={name}.__main__:plist2json
        plist22xml={name}.__main__:plist2xml
        plist22yaml={name}.__main__:plist2yaml
        xml22json={name}.__main__:xml2json
        xml22plist={name}.__main__:xml2plist
        xml22yaml={name}.__main__:xml2yaml
        yaml22json={name}.__main__:yaml2json
        yaml22plist={name}.__main__:yaml2plist
        yaml22xml={name}.__main__:yaml2xml
    """.format(name=NAME),
)
