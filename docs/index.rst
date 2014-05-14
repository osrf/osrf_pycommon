``osrf_pycommon``
=================

``osrf_pycommon`` is a python package which contains commonly used Python boilerplate code and patterns.
Things like ansi terminal coloring, capturing colored output from programs using subprocess, or even a simple logging system which provides some nice functionality over the built-in Python logging system.

The functionality provided here should be generic enough to be reused in arbitrary scenarios and should avoid bringing in dependencies which are not part of the standard Python library.
Where possible Windows and Linux/OS X should be supported, and where it cannot it should be gracefully degrading.
Code should be pure Python as well as Python 2 and Python 3 bilingual.

Contents:

.. toctree::
   :maxdepth: 2
