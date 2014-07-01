from osrf_pycommon.process_utils import asyncio
from osrf_pycommon.process_utils import async_execute_process

from .impl_aep_protocol import create_protocol

loop = asyncio.get_event_loop()


@asyncio.coroutine
def run(cmd, **kwargs):
    transport, protocol = yield asyncio.From(async_execute_process(
        create_protocol(), cmd, **kwargs))
    retcode = yield asyncio.From(protocol.complete)
    raise asyncio.Return(protocol.stdout_buffer, protocol.stderr_buffer,
                         retcode)