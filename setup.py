# -*- coding: utf-8 -*-
from distutils.core import setup

__author__ = "Shawn Lee"
__email__ = "shawn@143t.com"

setup(
    name="python-fram_logging",
    version="0.2.1",
    author="Shawn Lee",
    author_email="shawnl@143t.com",
    description="Fram standard py logging",
    keywords="fram logging",
    packages=["fram_logging"],
    package_dir={"fram_logging": "."},
    obsoletes="fram_logging",
    # Utility function to read the README file.
    # Used for the long_description.  It's nice, because now 1) we have a top
    # level README file and 2) it's easier to type in the README file than to
    # put a raw string in below.
    long_description=open("README").read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities"])
