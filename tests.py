
def it(expectation, test_input, test_output, transformer=lambda x: x):
    """Tests whether the expectation is valid by comparing the
       given test input to the test output. Test output may either
       be a value or function accepting one argument. Resembles
       the `it` function provided in the Jasmine JS testing module."""
    if transformer(test_input) == test_output or \
        test_input == test_output:
        print('Passed:', expectation)
    else:
        print('Failed:', expectation)

if __name__ == '__main__':
    it('returns true for given values', 0, 0)
    it('returns true for len function', [], 0, len)