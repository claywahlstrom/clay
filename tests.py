
def it(expectation, test_input, test_output, transformer=lambda x: x):
    """Tests whether the expectation is valid by comparing the
       given test input to the test output. Test output may either
       be a value or function accepting one argument. Resembles
       the `it` function provided in the Jasmine JS testing module."""
    result = transformer(test_input)
    if result == test_output:
        print(f'Passed: {expectation}')
    else:
        print(f'Failed: {expectation}. Expected {test_output} but found {result}')

if __name__ == '__main__':
    it('returns true for given values', 0, 0)
    it('returns true for len function', [], 0, len)
    it('returns true for 0 == 0', 0, 1)