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

from __future__ import print_function

import sys

try:
    # If Python is >= 3.4 asyncio is included
    # If Python is == 3.3 asyncio can be installed via pip
    from .async_execute_process_asyncio import async_execute_process
    from .async_execute_process_asyncio import loop
    from .async_execute_process_asyncio import asyncio
except (ImportError, SyntaxError):
    # If Python is < 3.3 then a SyntaxError will occur with asyncio
    # If Python is 3.3 and asyncio is not installed an ImportError occurs
    # In both cases, we must try to use trollius
    from .async_execute_process_trollius import async_execute_process
    from .async_execute_process_trollius import loop
    from .async_execute_process_trollius import asyncio

__all__ = [
    'async_execute_process',
    'AsyncSubprocessProtocol',
    'loop',
]


class AsyncSubprocessProtocol(asyncio.SubprocessProtocol):
    """
    Protocol to subclass to get events from :py:func:`async_execute_process`.

    When subclassing this Protocol class, you should override these functions:

    .. code-block:: python

        def on_stdout_received(self, data):
            # ...

        def on_stderr_received(self, data):
            # ...

        def on_process_exited(self, returncode):
            # ...


    By default these functions just print the data received from
    stdout and stderr and does nothing when the process exits.

    Data received by the ``on_stdout_received`` and ``on_stderr_received``
    functions is always in bytes (str in Python2 and bytes in Python3).
    Therefore, it may be necessary to call ``.decode()`` on the data before
    printing to the screen.

    Additionally, the data received will not be stripped of new lines, so take
    that into consideration when printing the result.

    You can also override these less commonly used functions:

    .. code-block:: python

        def on_stdout_open(self):
            # ...

        def on_stdout_close(self, exc):
            # ...

        def on_stderr_open(self):
            # ...

        def on_stderr_close(self, exc):
            # ...


    These functions are called when stdout/stderr are opened and closed, and
    can be useful when using pty's for example. The ``exc`` parameter of the
    ``*_close`` functions is None unless there was an exception.

    In addition to the overridable functions this class has a few useful
    public attributes.
    The ``stdin`` attribute is a reference to the PipeProto which follows the
    :py:class:`asyncio.WriteTransport` interface.
    The ``stdout`` and ``stderr`` attributes also reference their PipeProto.
    The ``complete`` attribute is a :py:class:`asyncio.Future` which is set to
    complete when the process exits and its result is the return code.

    The ``complete`` attribute can be used like this:

    .. code-block:: python

        @asyncio.coroutine
        def setup():
            transport, protocol = yield from async_execute_process(
                AsyncSubprocessProtocol, ['ls', '-G', '/usr'])
            retcode = yield from protocol.complete
            print("Exited with", retcode)

        # This will block until the protocol.complete Future is done.
        asyncio.get_event_loop().run_until_complete(setup())

    """
    def __init__(self, stdin=None, stdout=None, stderr=None):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.complete = asyncio.Future()
        asyncio.SubprocessProtocol.__init__(self)

    def connection_made(self, transport):
        self.transport = transport
        if self.stdin is None:
            self.stdin = self.transport.get_pipe_transport(0)
        if self.stdout is None:
            self.stdout = self.transport.get_pipe_transport(1)
        if self.stderr is None:
            self.stderr = self.transport.get_pipe_transport(2)

    def pipe_data_received(self, fd, data):
        # This function is only called when pty's are not being used
        stdout = self.stdout
        if not isinstance(stdout, int):
            stdout = 1
        if fd == stdout:
            self.on_stdout_received(data)
        else:
            assert fd == 2
            self.on_stderr_received(data)

    def _on_stdout_received(self, data):
        # print(data.__repr__())
        print(data.decode(), end='')

    def _on_stderr_received(self, data):
        # print(data.__repr__(), file=sys.stderr)
        print(data.decode(), end='', file=sys.stderr)

    def process_exited(self):
        retcode = self.transport.get_returncode()
        self.complete.set_result(retcode)
        self.on_process_exited(retcode)

    def on_process_exited(self, returncode):
        # print("Exited with", returncode)
        pass


if __name__ == '__main__':
    import os
    this_dir = os.path.dirname(os.path.abspath(__file__))

    import logging
    logging.basicConfig()
    # asyncio_log = logging.getLogger('asyncio')
    # asyncio_log.setLevel(logging.DEBUG)

    @asyncio.coroutine
    def setup():
        # transport, protocol = yield from async_execute_process(
        #     AsyncSubprocessProtocol, ['python', os.path.join(
        #         this_dir,
        #         '..',
        #         '..',
        #         'tests',
        #         'unit',
        #         'test_process_utils',
        #         'fixtures',
        #         'execute_process',
        #         'stdout_stderr_ordering.py')])
        # retcode = yield from protocol.complete
        # print("Exited with", retcode)
        # return retcode
        transport, protocol = yield asyncio.From(async_execute_process(
            AsyncSubprocessProtocol, ['python', os.path.join(
                this_dir,
                '..',
                '..',
                'tests',
                'unit',
                'test_process_utils',
                'fixtures',
                'execute_process',
                'stdout_stderr_ordering.py')]))
        retcode = yield asyncio.From(protocol.complete)
        print("Exited with", retcode)
        raise asyncio.Return(retcode)

    # This will block until the protocol.complete Future is done.
    loop.run_until_complete(setup())
