
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

def _show_success(expectation):
    print('Passed: {}'.format(expectation))

def _show_failure(expectation, expected, actual):
    print('Failed: {}. Expected {} but found {}' \
        .format(expectation, expected, actual))

def testif(expectation, test_input, test_output, raises=None, transformer=lambda x: x):
    """Tests whether the expectation is valid by comparing the
       given test input to the test output. Test output may either
       be a value or function accepting one argument."""
    if type(test_input).__name__ == 'function' and raises is not None: # lambda expressions
        if type(raises) != str:
            raise TypeError('raises must be of type string')
        has_raised = False
        is_correct_type = False
        ex_raised = None
        try:
            test_input()
        except Exception as ex:
            has_raised = True
            ex_raised = ex.__class__.__name__
            if ex_raised == raises:
                is_correct_type = True
                _show_success(expectation)

        if not has_raised or not is_correct_type:
            _show_failure(expectation, raises, ex_raised)
    else:
        if type(test_input).__name__ == 'function':
            test_input = test_input()
        result = transformer(test_input)
        if result == test_output:
            _show_success(expectation)
        else:
            _show_failure(expectation, test_output, result)

if __name__ == '__main__':
    testif('testif passes test for equal values', 0, 0)
    print('The next test should fail')
    testif('testif passes test for unequal values', 0, 1)
    print('The next test should fail')
    testif('testif passes test after applying transformer', [], 0, len)
    try:
        testif('testif passes test for raising division error', lambda: 0 / 0, None)
    except ZeroDivisionError: # pseudo branch
        print('Passed: testif passes test for raising division error when not specified')
    testif('testif passes test for raising division error when specified', lambda: 0 / 0, None, raises='ZeroDivisionError')
    print('The next test should fail')
    testif('testif passes test for not raising division error when specified', lambda: 0 / 1, None, raises='ZeroDivisionError')
    testif('testif passes test for lambda expression without error', lambda: 1 / 1, 1)
