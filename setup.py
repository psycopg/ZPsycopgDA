from setuptools import setup

# Get the version number from the package
f = open('Products/ZPsycopgDA/__init__.py')
try:
    for line in f:
        if line.startswith('__version__'):
            version = line.split()[-1].replace("'", "")
            break
    else:
        raise ValueError('__version__ not found')
finally:
    f.close()

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n'
)

setup(
    name='Products.ZPsycopgDA',
    version=version,
    description="Zope bindings for psycopg2.",
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Topic :: Database",
    ],
    keywords='',
    author='Federico Di Gregorio',
    author_email='fog@initd.org',
    url='http://initd.org/psycopg/',
    license='GPL with exceptions or ZPL',
    packages=['Products.ZPsycopgDA'],
    namespace_packages=['Products'],
    package_dir={'': '.'},
    package_data={
        'Products.ZPsycopgDA': ['dtml/*', 'icons/*']
    },
    include_package_data = True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
