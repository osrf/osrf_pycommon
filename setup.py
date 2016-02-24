from __future__ import print_function

import os
import shutil
import sys
import urllib
import zipfile

from setuptools import setup
from setuptools import find_packages

from distutils.command import clean
from setuptools.command import build_py
from setuptools.command import sdist


def get_custom_cmdclass():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    trollius_dir = os.path.join(this_dir, 'osrf_pycommon', 'vendor', 'trollius_helper', 'trollius')
    trollius_zip = 'trollius-2.1.zip'

    # Function for getting version 2.1 of trollius and embedding it in the vendor sub-package.
    def setup_embedded_trollius():
        if not os.path.exists(trollius_zip):
            url = "https://github.com/haypo/trollius/archive/trollius-2.1.zip"
            print("Retrieving trollius source from:", url)
            urllib.urlretrieve(url, trollius_zip)

        if not os.path.exists(trollius_dir):
            extraction_target = os.path.dirname(trollius_dir)
            print("Extracting trollius source to:", extraction_target)
            with zipfile.ZipFile(trollius_zip, 'r') as z:
                z.extractall(extraction_target)
            os.rename(os.path.join(extraction_target, 'trollius-trollius-2.1'), trollius_dir)

    def cleanup_embedded_trollius():
        if os.path.exists(trollius_zip):
            print("Removing:", trollius_zip)
            os.remove(trollius_zip)
        if os.path.exists(trollius_dir):
            print("Removing:", trollius_dir)
            shutil.rmtree(trollius_dir)

    # Custom sdist for setuptools which additionally embeds trollius in vendor.
    # This is only used when packaging a binary for Debian.
    class CustomSDist(sdist.sdist):
        def run(self):
            setup_embedded_trollius()
            return sdist.sdist.run(self)

    class CustomBuild(build_py.build_py):
        def finalize_options(self):
            build_py.build_py.finalize_options(self)
            trollius_files = []
            for root, dirnames, filenames in os.walk(trollius_dir):
                for filename in filenames:
                    trollius_files.append(os.path.join(root, filename))
            self.package_data['osrf_pycommon.vendor.trollius_helper'] = trollius_files

    class CustomClean(clean.clean):
        def run(self):
            cleanup_embedded_trollius()
            clean.clean.run(self)

    return {
        'sdist': CustomSDist,
        'build_py': CustomBuild,
        'clean': CustomClean,
    }

# If either 'sdist_dsc' or 'bdist_deb' are in the args, we're building a .deb.
building_debian = 'sdist_dsc' in sys.argv or 'bdist_deb' in sys.argv
cmdclass = {}
# If Python < 3.4, and packaging for Debian, setup an embedded copy of trollius.
if sys.version_info < (3, 4) and building_debian:
    cmdclass = get_custom_cmdclass()


install_requires = [
    'setuptools',
]
if sys.version_info < (3, 4):
    install_requires.append('trollius')

setup(
    name='osrf_pycommon',
    version='0.0.0',
    cmdclass=cmdclass,
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
        'License :: OSI Approved :: Apache 2.0',
        'Programming Language :: Python',
    ],
    description="Commonly needed Python modules, "
                "used by Python software developed at OSRF",
    license='Apache 2.0',
    test_suite='tests',
)
