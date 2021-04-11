#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import os
import re

NAME = 'yaplon'

readme_file = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'README.md')
try:
    from m2r import parse_from_file
    readme = parse_from_file(readme_file)
except ImportError:
    # m2r may not be installed in user environment
    with open(readme_file) as f:
        readme = f.read()


def get_version(*args):
    verstrline = open(os.path.join(NAME, "__init__.py"), "rt").read()
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
    directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(directory, *args)


setup(
    name=NAME,
    author='Adam Twardoch',
    author_email='adam+github@twardoch.com',
    url='https://twardoch.github.io/%s/' % (NAME),
    project_urls={
        'Source': "https://github.com/twardoch/%s/" % (NAME)
    },
    version=get_version(),
    license="MIT",
    description="Python 3-based commandline converter YAML ↔ JSON ↔ PLIST",
    long_description=readme,
    long_description_content_type='text/x-rst',
    python_requires='>=3.9',
    install_requires=get_requirements('requirements.txt'),
    extras_require={
        'dev': [
            'setuptools',
            'wheel',
            'pip',
            'twine>=3.2.0',
            'pyinstaller>=4.0',
            'm2r>=0.2.1'
        ]
    },
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
        %(name)s=%(name)s.__main__:cli
        json22plist=%(name)s.__main__:json2plist
        json22yaml=%(name)s.__main__:json2yaml
        plist22json=%(name)s.__main__:plist2json
        plist22yaml=%(name)s.__main__:plist2yaml
        yaml22json=%(name)s.__main__:yaml2json
        yaml22plist=%(name)s.__main__:yaml2plist
    ''' % {'name': NAME}
)
