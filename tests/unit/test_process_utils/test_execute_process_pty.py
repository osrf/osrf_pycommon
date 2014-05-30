import os
import sys
import unittest

from osrf_pycommon.process_utils import execute_process_pty

this_dir = os.path.dirname(os.path.abspath(__file__))

test_script = os.path.join(
    this_dir,
    'fixtures',
    'execute_process',
    'stdout_stderr_ordering.py')
python = sys.executable


def convert_file_linesep_with_pty_linesep(string):
    return string.replace("""
""", "\r\n")


class TestProcessUtilsExecuteNoPty(unittest.TestCase):
    def test__execute_process_pty_combined_unbuffered(self):
        exc_pty = execute_process_pty._execute_process_pty

        # Test ordering with stdout and stderr combined and Python unbuffered
        cmd = [python, "-u", test_script]
        result = ""
        for out, err, ret in exc_pty(cmd, None, None, False, True):
            if out is not None:
                result += out
            if err is not None:
                result += err
            if ret is not None:
                break
        expected = convert_file_linesep_with_pty_linesep("""\
out 1
err 1
out 2
""")
        self.assertEqual(expected, result)

    def test__execute_process_pty_unbuffered(self):
        exc_pty = execute_process_pty._execute_process_pty

        # Test ordering with stdout and stderr combined and Python unbuffered
        cmd = [python, "-u", test_script]
        result = ""
        for out, err, ret in exc_pty(cmd, None, None, False, False):
            if out is not None:
                result += out
            if err is not None:
                result += err
            if ret is not None:
                break
        expected = convert_file_linesep_with_pty_linesep("""\
out 1
err 1
out 2
""")
        self.assertEqual(expected, result)

    def test__execute_process_pty_combined(self):
        exc_pty = execute_process_pty._execute_process_pty

        # Test ordering with stdout and stderr combined
        cmd = [python, test_script]
        result = ""
        for out, err, ret in exc_pty(cmd, None, None, False, True):
            if out is not None:
                result += out
            if err is not None:
                result += err
            if ret is not None:
                break
        expected = convert_file_linesep_with_pty_linesep("""\
out 1
err 1
out 2
""")
        self.assertEqual(expected, result)

    def test__execute_process_pty(self):
        exc_pty = execute_process_pty._execute_process_pty

        # Test ordering with stdout and stderr separate
        cmd = [python, test_script]
        result = ""
        for out, err, ret in exc_pty(cmd, None, None, False, False):
            if out is not None:
                result += out
            if err is not None:
                result += err
            if ret is not None:
                break
        expected = convert_file_linesep_with_pty_linesep("""\
out 1
err 1
out 2
""")
        self.assertEqual(expected, result)
