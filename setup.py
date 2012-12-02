from setuptools import setup, find_packages
import os

version = '2.4.4'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='ZPsycopgDA',
      version=version,
      description="Zope bindings for psycopg2.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Federico Di Gregorio',
      author_email='fog@initd.org',
      url='http://initd.org/psycopg/',
      license='GPL with exceptions or ZPL',
      packages=find_packages('.'),
      package_dir = {'': '.'},
      namespace_packages=['ZPsycopgDA'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
