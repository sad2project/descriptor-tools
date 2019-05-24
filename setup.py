import codecs
import os
from setuptools import setup, find_packages


HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()

setup(
  name='descriptor_tools',
  packages=find_packages(where="src"),
  package_dir={"": "src"},
  version='1.1.0',
  description='A collection of classes and functions to make the creation of descriptors simpler and quicker',
  author='Jacob Zimmerman',
  author_email='sad2project@gmail.com',
  url='https://github.com/sad2project/descriptor-tools',
  download_url='https://github.com/sad2project/descriptor-tools/tarball/1.1.0',
  keywords=['descriptors', 'properties'],
  classifiers=["Development Status :: 5 - Production/Stable",
                 "Intended Audience :: Developers",
                 "Natural Language :: English",
                 "Operating System :: OS Independent",
                 "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
                 "Programming Language :: Python",
                 "Programming Language :: Python :: 3.3",
                 "Programming Language :: Python :: 3.4",
                 "Programming Language :: Python :: 3.5",
                 "Programming Language :: Python :: 3.6",
                 "Programming Language :: Python :: 3.7",
                 "Programming Language :: Python :: Implementation :: CPython",
                 "Programming Language :: Python :: Implementation :: PyPy",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 ],
  license="CC0 1.0 Universal",
  long_description=read("README.md"),
  install_requires=[]
)
