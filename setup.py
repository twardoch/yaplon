#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from cx_Freeze import setup, Executable
from os import path
import re

with open(path.join(path.abspath(path.dirname(__file__)), 'README.md')) as f:
    long_description = f.read()


def get_version(*args):
    verstrline = open("yaplon/__init__.py", "rt").read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        return mo.group(1)
    else:
        return "undefined"


def get_requirements(*args):
    """Get requirements from pip requirement files."""
    requirements = set()
    with open(get_absolute_path(*args)) as handle:
        for line in handle:
            # Strip comments.
            line = re.sub(r'^#.*|\s#.*', '', line)
            # Ignore empty lines
            if line and not line.isspace():
                requirements.add(re.sub(r'\s+', '', line))
    return sorted(requirements)


def get_absolute_path(*args):
    """Transform relative pathnames into absolute pathnames."""
    directory = path.dirname(path.abspath(__file__))
    return path.join(directory, *args)


setup(
    name='yaplon',
    author='Adam Twardoch',
    author_email='adam+github@twardoch.com',
    url='https://twardoch.github.io/yaplon/',
    project_urls={
        'Source': "https://github.com/twardoch/yaplon"
    },
    version=get_version(),
    license="MIT",
    description="Python 3-based commandline converter YAML ↔ JSON ↔ PLIST",
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.7',
    install_requires=get_requirements('requirements.txt'),
    packages=find_packages(),
    classifiers=[
        'Environment :: Console',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='yaml json plist convert cli',
    entry_points='''
        [console_scripts]
        yaplon=yaplon.__main__:cli
        json22plist=yaplon.__main__:json2plist
        json22yaml=yaplon.__main__:json2yaml
        plist22json=yaplon.__main__:plist2json
        plist22yaml=yaplon.__main__:plist2yaml
        yaml22json=yaplon.__main__:yaml2json
        yaml22plist=yaplon.__main__:yaml2plist
    ''',
    options={
        "build_exe": {
            "packages": ["os"],
            "excludes": ["tkinter"]
        }
    },
    executables=[
        Executable(
            path.join("yaplon", "__main__.py"),
            targetName="yaplon.exe",
            base=None
        )
    ]
)
