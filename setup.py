#!/usr/bin/env python

# Two environment variables influence this script.
#
# GEOS_LIBRARY_PATH: a path to a GEOS C shared library.
#
# GEOS_CONFIG: the path to a geos-config program that points to GEOS version,
# headers, and libraries.
#
# NB: within this setup scripts, software versions are evaluated according
# to https://www.python.org/dev/peps/pep-0440/.

from sys import version_info as v, warnoptions

if any([v < (2, 6), (3,) < v < (3, 3)]):
    raise Exception("Unsupported Python version %d.%d. Requires Python >= 2.6 "
                    "or >= 3.3." % v[:2])

import logging
import os

# If possible, use setuptools
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext

# Prevent numpy from thinking it is still in its setup process:
__builtins__.__NUMPY_SETUP__ = False


class BuildExtNumpyInc(build_ext):
    def build_extensions(self):
        from numpy.distutils.misc_util import get_numpy_include_dirs
        for e in self.extensions:
            e.include_dirs.extend(get_numpy_include_dirs())

        build_ext.build_extensions(self)


logging.basicConfig()
log = logging.getLogger(__file__)

# python -W all setup.py ...
if 'all' in warnoptions:
    log.level = logging.DEBUG


# Handle UTF-8 encoding of certain text files.
open_kwds = {}
if v >= (3,):
    open_kwds['encoding'] = 'utf-8'

with open('README.rst', 'r', **open_kwds) as fp:
    readme = fp.read()

with open('CREDITS.txt', 'r', **open_kwds) as fp:
    credits = fp.read()

with open('CHANGES.txt', 'r', **open_kwds) as fp:
    changes = fp.read()

long_description = readme + '\n\n' + credits + '\n\n' + changes

# Prepare build opts and args for the speedups extension module.
include_dirs = []
library_dirs = []
libraries = ['geos_c']
extra_link_args = []

ext_modules = [
    Extension(
        "shapely.speedups._speedups",
        ["shapely/speedups/_speedups.pyx"],
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=libraries,
    ),
    Extension(
        "shapely.vectorized._vectorized",
        sources=["shapely/vectorized/_vectorized.pyx"],
        libraries=libraries,
    ),
]

setup(
    name='Shapely',
    requires=['Python (>=2.6)', 'libgeos_c (>=3.3)'],
    use_scm_version={
        'version_scheme': 'guess-next-dev',
        'local_scheme': 'dirty-tag',
        'write_to': 'shapely/_version.py'
    },

    setup_requires=[
        'setuptools>=18.0',
        'setuptools-scm>1.5.4',
        'Cython>=0.19.2',
        'numpy>=1.8.0',
        'pytest-runner',
    ],
    install_requires=[
        'numpy>=1.8.0'
    ],
    extras_require={
        "tests:python_version=='2.6'": ["unittest2"],
        "docs": [
            "sphinx>=1.2",
            "descartes>=1.0.1",
            "matplotlib>=1.2"
        ],
        "tests": ['pytest>=1.0'],
    },
    description='Geometric objects, predicates, and operations',
    license='BSD',
    keywords='geometry topology gis',
    author='Sean Gillies',
    author_email='sean.gillies@gmail.com',
    maintainer='Sean Gillies',
    maintainer_email='sean.gillies@gmail.com',
    url='https://github.com/Toblerity/Shapely',
    long_description=long_description,
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", 'tests']),
    ext_modules=ext_modules,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    cmdclass={'build_ext': BuildExtNumpyInc},
    package_data={'': ['*.pxi'],},
)
