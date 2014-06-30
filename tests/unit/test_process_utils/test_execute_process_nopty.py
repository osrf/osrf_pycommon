import os
import sys
import unittest

from osrf_pycommon.process_utils import execute_process_nopty

this_dir = os.path.dirname(os.path.abspath(__file__))

test_script = os.path.join(
    this_dir,
    'fixtures',
    'execute_process',
    'stdout_stderr_ordering.py')
python = sys.executable


class TestProcessUtilsExecuteNoPty(unittest.TestCase):
    def test__process_incomming_lines(self):
        pil = execute_process_nopty._process_incoming_lines
        nl = os.linesep

        # Test with no left overs and no new incoming
        left_overs = b''
        incoming = b''
        self.assertEqual((None, left_overs), pil(incoming, left_overs))

        # Test with left overs, but no new incoming
        left_overs = b'something'
        incoming = b''
        self.assertEqual(('', left_overs), pil(incoming, left_overs))

        # Test with no left overs, but new incoming
        left_overs = b''
        incoming = nl.join(['one', 'two']).encode('utf-8')
        self.assertEqual(('one' + nl, b'two'), pil(incoming, left_overs))

        # Test with left overs and new incoming with prefixed nl
        left_overs = b'something'
        incoming = (nl + 'else').encode('utf-8')
        expected = ('something' + nl, b'else')
        self.assertEqual(expected, pil(incoming, left_overs))

    def test__execute_process_nopty_combined_unbuffered(self):
        exc_nopty = execute_process_nopty._execute_process_nopty

        # Test ordering with stdout and stderr combined and Python unbuffered
        cmd = [python, "-u", test_script]
        result = ""
        for out, err, ret in exc_nopty(cmd, None, None, False, True):
            if out is not None:
                result += out
            if err is not None:
                result += err
            if ret is not None:
                break
        expected = """\
out 1
err 1
out 2
"""
        self.assertEqual(expected, result)

    def test__execute_process_nopty_unbuffered(self):
        exc_nopty = execute_process_nopty._execute_process_nopty

        # Test ordering with stdout and stderr combined and Python unbuffered
        cmd = [python, "-u", test_script]
        result = ""
        for out, err, ret in exc_nopty(cmd, None, None, False, False):
            if out is not None:
                result += out
            if err is not None:
                result += err
            if ret is not None:
                break
        expected = """\
out 1
err 1
out 2
"""
        # I expect the output not to be correct; not sure this is reliable
        self.assertNotEqual(expected, result)

    def test__execute_process_nopty_combined(self):
        exc_nopty = execute_process_nopty._execute_process_nopty

        # Test ordering with stdout and stderr combined
        cmd = [python, test_script]
        result = ""
        for out, err, ret in exc_nopty(cmd, None, None, False, True):
            if out is not None:
                result += out
            if err is not None:
                result += err
            if ret is not None:
                break
        expected = """\
out 1
err 1
out 2
"""
        # I expect the output not to be correct; not sure this is reliable
        self.assertNotEqual(expected, result)

    def test__execute_process_nopty(self):
        exc_nopty = execute_process_nopty._execute_process_nopty

        # Test ordering with stdout and stderr separate
        cmd = [python, test_script]
        result = ""
        for out, err, ret in exc_nopty(cmd, None, None, False, False):
            if out is not None:
                result += out
            if err is not None:
                result += err
            if ret is not None:
                break
        expected = """\
out 1
err 1
out 2
"""
        # I expect the output not to be correct; not sure this is reliable
        self.assertNotEqual(expected, result)
