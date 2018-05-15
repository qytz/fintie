#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup
from pip.req import parse_requirements

with open('README.rst', 'r', encoding='utf-8') as readme_file:
    readme = readme_file.read()

requirements = [str(ir.req) for ir in parse_requirements(
    "requirements.txt", session=False)]

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'csdaily', '__version__.py'), 'r', encoding='utf-8') as f:
    exec(f.read(), about)

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()
with open('CHANGELOG.rst', 'r', encoding='utf-8') as f:
    changelog = f.read()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme + '\n\n' + changelog,
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=['csdaily'],
    package_dir={'csdaily': 'csdaily'},
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.5',
    license=about['__license__'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'csdaily = csdaily.__main__:main'
        ]
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        # 'Natural Language :: Simplified Chinese',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
)
