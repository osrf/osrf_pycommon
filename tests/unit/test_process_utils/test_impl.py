from __future__ import unicode_literals

import os
import unittest

from osrf_pycommon.process_utils import impl

this_dir = os.path.dirname(os.path.abspath(__file__))


class TestProcessUtilsImpl(unittest.TestCase):
    def test_which(self):
        which = impl.which
        j = os.path.join
        prefix = j(this_dir, 'fixtures', 'impl_which')
        paths = [
            j(prefix, 'usr', 'local', 'bin'),
            j(prefix, 'usr', 'bin'),
            j(prefix, 'bin'),
        ]
        # bin_only exists +x in bin only
        expected = j(prefix, 'bin', 'bin_only')
        self.assertEqual(expected, which('bin_only', paths))
        self.assertEqual(expected, which(expected, paths))
        # exc1 exists +x in bin and usr/bin
        expected = j(prefix, 'usr', 'bin', 'exc1')
        self.assertEqual(expected, which('exc1', paths))
        self.assertEqual(expected, which(expected, paths))
        # exc2 exists +x in bin and usr/bin, but -x in usr/local/bin
        expected = j(prefix, 'usr', 'bin', 'exc2')
        self.assertEqual(expected, which('exc2', paths))
        self.assertEqual(expected, which(expected, paths))
        # Same as above, with PATH
        orig_path = os.environ['PATH']
        try:
            os.environ['PATH'] = os.pathsep.join(paths)
            # bin_only exists +x in bin only
            expected = j(prefix, 'bin', 'bin_only')
            self.assertEqual(expected, which('bin_only'))
            self.assertEqual(expected, which(expected))
            # exc1 exists +x in bin and usr/bin
            expected = j(prefix, 'usr', 'bin', 'exc1')
            self.assertEqual(expected, which('exc1'))
            self.assertEqual(expected, which(expected))
            # exc2 exists +x in bin and usr/bin, but -x in usr/local/bin
            expected = j(prefix, 'usr', 'bin', 'exc2')
            self.assertEqual(expected, which('exc2'))
            self.assertEqual(expected, which(expected))
        finally:
            os.environ['PATH'] = orig_path
        # Test error cases
        with self.assertRaisesRegexp(ValueError, "is not a string"):
            which(1, paths)
        which(str("exc1"), paths)  # Make sure unicode/str works
        with self.assertRaisesRegexp(ValueError, "Relative path given"):
            which(j("path", "program"), paths)
        with self.assertRaisesRegexp(ValueError, "is not a list"):
            which("dosentmatter", 'not a list')
        which("doesntmatter", ('/make/sure', '/tuples/are/ok'))
        with self.assertRaisesRegexp(ValueError, "Non absolute path"):
            which("dosentmatter", ['relative/path'])
