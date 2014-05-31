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

from .execute_process_nopty import _execute_process_nopty
try:
    from .execute_process_pty import _execute_process_pty
except ImportError:
    # pty doesn't work on Windows, it will fail to import
    # so fallback to non pty implementation
    _execute_process_pty = None

try:
    _basestring = basestring  # Python 2
except NameError:
    _basestring = str  # Python 3


def execute_process(cmd, cwd=None, env=None, shell=False, emulate_tty=False):
    """Executes a command with arguments and returns output line by line.

    All arguments, except ``emulate_tty``, are passed directly to
    :py:class:`subprocess.Popen`.

    ``execute_process`` returns a generator which yields the output, line by
    line, until the subprocess finishes at which point the return code
    is yielded.

    This is an example of how this function should be used:

    .. code-block:: python

        from osrf_pycommon.process_utils import execute_process

        cmd = ['ls', '-G']
        for line in execute_process(cmd, cwd='/usr'):
            if isinstance(line, int):
                # This is a return code, the command has exited
                print("'{0}' exited with: {1}".format(' '.join(cmd), line))
                continue  # break would also be appropriate here
            # Then print it to the screen
            print(line, end='')

    ``stdout`` and ``stderr`` are always captured together and returned line
    by line through the returned generator.
    New line characters are preserved in the output, so if re-printing the data
    take care to use ``end=''`` or first ``rstrip`` the output lines.

    When ``emulate_tty`` is used on Unix systems, commands will identify that
    they are on a tty and should output color to the screen as if you were
    running it on the terminal, and therefore there should not be any need to
    pass arguments like ``-c color.ui=always`` to commands like ``git``.
    Additionally, programs might also behave differently in when
    ``emulate_tty`` is being used, for example, Python will default to
    unbuffered output when it detects a tty.

    ``emulate_tty`` works by using psuedo-terminals on Unix machines, and so
    if you are running this command many times in parallel (like hundreds
    of times) then you may get one of a few different :py:exc:`OSError`'s.
    For example, "OSError: [Errno 24] Too many open files: '/dev/ttyp0'" or
    "OSError: out of pty devices".
    You should also be aware that you share pty devices with the rest of the
    system, so even if you are not using a lot, it is possible to get
    this error.
    You can catch this error before getting data from the generator, so when
    using ``emulate_tty`` you might want to do something like this:

    .. code-block:: python

        from osrf_pycommon.process_utils import execute_process

        cmd = ['ls', '-G', '/usr']
        try:
            output = execute_process(cmd, emulate_tty=True)
        except OSError:
            output = execute_process(cmd, emulate_tty=False)
        for line in output:
            if isinstance(line, int):
                print("'{0}' exited with: {1}".format(' '.join(cmd), line))
                continue
            print(line, end='')

    This way if a pty cannot be opened in order to emulate the tty then you
    can try again without emulation, and any other :py:exc:`OSError` should
    raise again with ``emulate_tty`` set to ``False``.
    Obviously, you only want to do this if emulating the tty is non-critical
    to your processing, like when you are using it to capture color.

    Any color information that the command outputs as ANSI escape sequences
    is captured by this command.
    That way you can print the output to the screen and preserve the color
    formatting.

    If you do not want color to be in the output, then try setting
    ``emulate_tty`` to ``False``, but that does not guarantee that there is no
    color in the output, instead it only will cause called processes to
    identify that they are not being run in a terminal.
    Most well behaved programs will not output color if they detect that
    they are not being executed in a terminal, but you shouldn't rely on that.

    If you want to ensure there is no color in the output from an executed
    process, then use this function:

    :py:func:`osrf_pycommon.terminal_color.remove_ansi_escape_senquences`

    Exceptions can be raised by functions called by the implementation,
    for example, :py:class:`subprocess.Popen` can raise an :py:exc:`OSError`
    when the given command is not found.
    If you want to check for the existence of an executable on the path,
    see: :py:func:`which`.
    However, this function itself does not raise any special exceptions.

    :param list cmd: list of strings with the first item being a command
        and subsequent items being any arguments to that command;
        passed directly to :py:class:`subprocess.Popen`.
    :param str cwd: path in which to run the command, defaults to None which
        means :py:func:`os.getcwd` is used;
        passed directly to :py:class:`subprocess.Popen`.
    :param dict env: environment dictionary to use for executing the command,
        default is None which uses the :py:obj:`os.environ` environment;
        passed directly to :py:class:`subprocess.Popen`.
    :param bool shell: If True the system shell is used to evaluate the
        command, default is False;
        passed directly to :py:class:`subprocess.Popen`.
    :param bool emulate_tty: If True attempts to use a pty to convince
        subprocess's that they are being run in a terminal. Typically this is
        useful for capturing colorized output from commands. This does not
        work on Windows (no pty's), so it is considered False even when True.
        Defaults to False.
    :returns: a generator which yields output from the command line by line
    :rtype: generator which yields strings
    """
    exp_func = _execute_process_nopty
    if emulate_tty and _execute_process_pty is not None:
        exp_func = _execute_process_pty
    for out, err, ret in exp_func(cmd, cwd, env, shell, stderr_to_stdout=True):
        if ret is None:
            yield out
        yield ret


def execute_process_split(
    cmd, cwd=None, env=None, shell=False, emulate_tty=False
):
    """:py:func:`execute_process`, except ``stderr`` is returned separately.

    Instead of yielding output line by line until yielding a return code, this
    function always a triplet of ``stdout``, ``stderr``, and return code.
    Each time only one of the three will not be None.
    Once you receive a non-None return code (type will be int) there will be no
    more ``stdout`` or ``stderr``.
    Therefore you can use the command like this:

    .. code-block:: python

        import sys
        from osrf_pycommon.process_utils import execute_process_split

        cmd = ['ls', '-G']
        for out, err, ret in execute_process_split(cmd, cwd='/usr'):
            if ret is not None:
                # This is a return code, the command has exited
                print("'{0}' exited with: {1}".format(' '.join(cmd), ret))
            elif out is not None:
                print(out, end='')
            elif err is not None:
                print(err, end='', file=sys.stderr)

    When using this, it is possible that the ``stdout`` and ``stderr`` data can
    be returned in a different order than what would happen on the terminal.
    This is due to the fact that the subprocess is given different buffers for
    ``stdout`` and ``stderr`` and so there is a race condition on the
    subprocess writing to the different buffers and this command reading the
    buffers.
    This can be avoided in most scenarios by using ``emulate_tty``, because of
    the use of ``pty``'s, though the ordering can still not be guaranteed and
    the number of ``pty``'s is finite as explained in the documentation for
    :py:func:`execute_process`.
    For situations where output ordering between ``stdout`` and ``stderr`` are
    critical, they should not be returned separately and instead should share
    one buffer, and so :py:func:`execute_process` should be used.

    For all other parameters and documentation see: :py:func:`execute_process`
    """
    exp_func = _execute_process_nopty
    if emulate_tty and _execute_process_pty is not None:
        exp_func = _execute_process_pty
    return exp_func(cmd, cwd, env, shell, stderr_to_stdout=True)


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
