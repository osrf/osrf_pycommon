# Copyright 2014 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

try:
    _basestring = basestring  # Python 2
except NameError:
    _basestring = str  # Python 3


def which(program, paths=None):
    """Custom version of the ``which`` built-in shell command.

    Searches the paths in the ``PATH`` environment variable for a given
    executable name. It returns the full path to the first instance of the
    executable found or None if it was not found.
    Only files in the paths marked as executable are considered.

    If an absolute path is given and the path exists and is executable, it is
    returned as passed, otherwise None is returned. Either way no searching is
    done.

    If a relative path is given then a :py:exc:`ValueError` is raised.

    :param str program: name of the executable to find
    :param paths: If a list of strings given, use that instead of paths in
        PATH, default is None. Given strings must be absolute, or a
        :py:exc:`ValueError` is raised.
    :type paths: list or None
    :returns: Full path to the first instance of the executable, or None
    :rtype: str or None
    :raises: :py:exc:`ValueError` if a relative path or any non-string is given
    """
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    if not isinstance(program, _basestring):
        raise ValueError("Parameter 'program' is not a string: '{0}'"
                         .format(program))

    if os.path.isabs(program):
        if is_exe(program):
            return program
        return None
    else:
        head, tail = os.path.split(program)
        if head and tail:
            raise ValueError("Relative path given: '{0}'".format(program))

        if paths is None:
            paths = os.environ.get('PATH', os.defpath).split(os.pathsep)
        else:
            if not isinstance(paths, (list, tuple)):
                raise ValueError("Parameter 'paths' is not a list: '{0}'"
                                 .format(paths))
            for path in paths:
                if not os.path.isabs(path):
                    raise ValueError("Non absolute path given: '{0}'"
                                     .format(path))
        for path in paths:
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None
