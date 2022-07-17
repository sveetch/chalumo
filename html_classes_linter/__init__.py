"""A simple script to lint, diff or reformat HTML 'class' attribute values"""
from __future__ import absolute_import, unicode_literals

import os
from setuptools.config import read_configuration

import pkg_resources

PROJECT_DIR = os.path.join(os.path.dirname(__file__), "..")


def _extract_version(package_name):
    """
    Get package version from installed distribution or configuration file if not
    installed
    """
    try:
        return pkg_resources.get_distribution(package_name).version
    except pkg_resources.DistributionNotFound:
        _conf = read_configuration(os.path.join(PROJECT_DIR, "setup.cfg"))
    return _conf["metadata"]["version"]

__pkgname__ = "html-classes-linter"
__version__ = _extract_version(__pkgname__)