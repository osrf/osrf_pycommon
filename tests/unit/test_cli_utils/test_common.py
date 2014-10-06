from osrf_pycommon.cli_utils import common


def test_extract_jobs_flags():
    extract_jobs_flags = common.extract_jobs_flags
    valid_mflags = [
        '-j8 -l8', 'j8 ', '-j', 'j', '-l8', 'l8',
        '-l', 'l', '-j18', ' -j8 l9', '-j1 -l1',
        '--jobs=8', '--jobs 8', '--jobs', '--load-average',
        '--load-average=8', '--load-average 8', '--jobs=8 -l9'
    ]
    results = [
        '-j8 -l8', 'j8', '-j', 'j', '-l8', 'l8',
        '-l', 'l', '-j18', '-j8 l9', '-j1 -l1',
        '--jobs=8', '--jobs 8', '--jobs', '--load-average',
        '--load-average=8', '--load-average 8', '--jobs=8 -l9'
    ]
    for mflag, result in zip(valid_mflags, results):
        match = extract_jobs_flags(mflag)
        assert match == result, "should match '{0}'".format(mflag)
        print('--')
        print("input:    '{0}'".format(mflag))
        print("matched:  '{0}'".format(match))
        print("expected: '{0}'".format(result))
    invalid_mflags = ['', '--jobs= 8', '--jobs8']
    for mflag in invalid_mflags:
        match = extract_jobs_flags(mflag)
        assert match is None, "should not match '{0}'".format(mflag)


def test_extract_argument_group():
    extract_argument_group = common.extract_argument_group
    # Example 1 from docstring
    args = ['foo', '--args', 'bar', '--baz']
    expected = (['foo'], ['bar', '--baz'])
    results = extract_argument_group(args, '--args')
    assert expected == results, (args, expected, results)
    # Example 2 from docstring
    args = ['foo', '--args', 'bar', '--baz', '---', '--', '--foo-option']
    expected = (['foo', '--foo-option'], ['bar', '--baz', '--'])
    results = extract_argument_group(args, '--args')
    assert expected == results, (args, expected, results)
    # Example 3 from docstring
    args = ['foo',
            '--args', 'ping', '--',
            'bar',
            '--args', 'pong', '--',
            'baz',
            '--args', '--']
    expected = (['foo', 'bar', 'baz'], ['ping', 'pong'])
    results = extract_argument_group(args, '--args')
    assert expected == results, (args, expected, results)
    # Example with delimeter but no arguments
    args = ['foo', '--args']
    expected = (['foo'], [])
    results = extract_argument_group(args, '--args')
    assert expected == results, (args, expected, results)
    # Example with no delimeter
    args = ['foo', 'bar']
    expected = (['foo', 'bar'], [])
    results = extract_argument_group(args, '--args')
    assert expected == results, (args, expected, results)
