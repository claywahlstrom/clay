
import inspect as _inspect

_stack = _inspect.stack()

if _stack[-1].code_context is None:
    # if __name__ == '__main__' equivalent
    _frame = _stack[0]
else:
    # if imported from another module
    _frame = _stack[-1]

MODULE = _inspect.getmodulename(_frame[1]) + '.py'

print()
print('Running tests for "{}"...'.format(MODULE))
print()

def testif(expectation, test_input, test_output, transformer=lambda x: x):
    """Tests whether the expectation is valid by comparing the
       given test input to the test output. Test output may either
       be a value or function accepting one argument."""
    result = transformer(test_input)
    if result == test_output:
        print('Passed: {}'.format(expectation))
    else:
        print('Failed: {}. Expected {} but found {}' \
            .format(expectation, test_output, result))

if __name__ == '__main__':
    testif('returns true for given values', 0, 0)
    testif('returns true for len function', [], 0, len)
    testif('returns true for 0 == 0', 0, 1)
