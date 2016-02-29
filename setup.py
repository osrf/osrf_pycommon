import sys

from setuptools import setup
from setuptools import find_packages


install_requires = [
    'setuptools',
]
if sys.version_info < (3, 4):
    install_requires.append('trollius')

setup(
    name='osrf_pycommon',
    version='0.1.0',
    packages=find_packages(exclude=['tests', 'docs']),
    install_requires=install_requires,
    author='William Woodall',
    author_email='william@osrfoundation.org',
    maintainer='William Woodall',
    maintainer_email='william@osrfoundation.org',
    url='http://osrf-pycommon.readthedocs.org/',
    keywords=['osrf', 'utilities'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ],
    description="Commonly needed Python modules, "
                "used by Python software developed at OSRF",
    license='Apache 2.0',
    test_suite='tests',
)
