import os

from setuptools import find_packages
from setuptools import setup


def _read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as fp:
        return fp.read()


long_description = (
    _read('README.rst')
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    _read('CONTRIBUTORS.txt')
    + '\n' +
    _read('CHANGES.txt')
    + '\n'
)

setup(
    name='Products.ZPsycopgDA',
    version='3.0b1',
    license='ZPL 2.1',
    license_files=['LICENSE*'],
    author='Federico Di Gregorio',
    author_email='fog@initd.org',
    maintainer='Jens Vagelpohl',
    maintainer_email='jens@dataflake.org',
    url='https://github.com/dataflake/Products.ZPsycopgDA',
    project_urls={
        'Documentation': 'https://zpsycopgda.readthedocs.io',
        'Issue Tracker': ('https://github.com/dataflake'
                          '/Products.ZPsycopgDA/issues'),
        'Sources': 'https://github.com/zopefoundation/Products.ZPsycopgDA',
    },
    description='Zope database adapter for PostGreSQL',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Zope',
        'Framework :: Zope :: 4',
        'Framework :: Zope :: 5',
        'License :: OSI Approved :: Zope Public License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Database',
        'Topic :: Database :: Front-Ends',
    ],
    packages=find_packages('src'),
    include_package_data=True,
    namespace_packages=['Products'],
    package_dir={'': 'src'},
    zip_safe=False,
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
    install_requires=[
        'setuptools',
        'psycopg2; python_version>="3.6"',
        'psycopg2 < 2.9; python_version<="3.5"',
        'Zope',
        'Products.ZSQLMethods',
    ],
    extras_require={
        'docs': ['Sphinx', 'sphinx_rtd_theme'],
    },
)
