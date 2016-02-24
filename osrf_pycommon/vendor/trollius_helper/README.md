This "trollius" sub-package in the `osrf_pycommon.vendor` package is designed to allow an embedded copy of trollius.
This is requried when a suitable dependency on trollius cannot be acheived through normal channels.
For example, on Ubuntu Trusty there is no debian binary package for python-trollius.
So inorder to release a binary package of osrf_pycommon we need to embed a version of trollius.

For most systems this is not necessary, as osrf_pycommon is installed from pip and trollius can be just a normal dependency.

This sub-package works like so:

- the `__init__.py` file will try to import trollius normally
- if that fails it will check for an embedded version of trollius
- if that exists it will add that folder to the path and try to import again

In order for this embedded version to work it must be placed in a folder called `trollius` in this folder.
It must also have the layout of trollius's source repository as of 2.1, i.e. the importable source is in the root.

By default, the 2.1 release of trollius will be cloned (or fetched and extracted) to this folder before release.
