# encoding=utf-8


def assert_equal(name, expected, actual):
    if expected != actual:
        print('%s expected: %s  actual: %s' % (name, expected, actual))
