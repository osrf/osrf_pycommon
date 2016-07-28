import os
import sys
import subprocess


def test_flake8():
    """Test source code for pyFlakes and PEP8 conformance"""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(this_dir, '..', 'osrf_pycommon')
    cmd = ['flake8', source_dir, '--count']
    if sys.version_info < (3,4):
        # Unless Python3, skip files with new syntax, like `yield from`
        cmd.append('--exclude=*async_execute_process_asyncio/impl.py')
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = p.communicate()
    print(stdout)
    assert p.returncode == 0, \
        "Command '{0}' returned non-zero exit code '{1}'".format(' '.join(cmd), p.returncode)
