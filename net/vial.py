
"""
Helpers for the Pallets Flask(c) web framework

"""

import flask

import clay.models
import clay.text

class Html(clay.models.Static):

    """Helper for generating HTML inside views"""

    @staticmethod
    def get_newlines_string(string):
        """Returns the HTML newlines string using the given a string"""
        if not isinstance(string, bytes) and not isinstance(string, str):
            raise TypeError('string must of type bytes or str')

        if isinstance(string, bytes):
            if b'\r' in string:
                # remove \r from string
                string = string.replace(b'\r', b'')
            return string.replace(b'\n', b'<br />')
        elif isinstance(string, str):
            if '\r' in string:
                # remove \r from string
                string = string.replace('\r', '')
            return string.replace('\n', '<br />')
        else:
            raise RuntimeError('this point shall not be reached')

    @staticmethod
    def replace_md_with_anchor(md_str):
        """Replaces markdown link styles with externally linked HTML anchor tags"""
        import re
        anchor_str = md_str
        # restrict findall to only take chars inside explicit [] and ()
        # by using [^\[]
        groups = re.findall('\[([^\[]*)\]\(([^\[]*)\)', md_str)
        for text, link in groups:
            reconstructed = '[{}]({})'.format(text, link)
            anchored = '<a target="_blank" href="{}">{}~^</a>'.format(link, text)
            anchor_str = anchor_str.replace(reconstructed, anchored)
        return anchor_str

    @staticmethod
    def label(name, text=None):
        """Returns markup for the label element `name`, `text` defaults to `name`"""
        text = text if text is not None else name
        return '<label for="{}">{}</label>'.format(name, text)

    @staticmethod
    def input(name, type, value='', attrs={}):
        """Returns markup for the input element `name` of type `type`,
        value `value, and attributes `attrs`"""
        attribs = ''.join('{}="{}" '.format(key, value) for key, value in attrs.items())
        return '<input type="{0}" id="{1}" name="{1}" value="{2}" {3}/>' \
            .format(type, name, value, attribs)

    @staticmethod
    def checkbox(name, checked=False):
        """Returns markup for the checkbox input element `name`"""
        attrs = {'checked': 'checked'} if checked else {}
        return Html.input(name, 'checkbox', attrs=attrs)

    @staticmethod
    def date(name, value='', attrs={}):
        """Returns markup for the date input element `name` of value `value`,
        and attributes `attrs`"""
        return Html.input(name, 'date', value=value.replace('/', '-'), attrs=attrs)

    @staticmethod
    def hidden(name, value=''):
        """Returns markup for the hidden input element `name` of value `value`"""
        return Html.input(name, 'hidden', value=value)

    @staticmethod
    def submit(value='', attrs={}):
        """Returns markup for the submit input element of value `value` and attributes `attrs`"""
        attribs = ''.join('{}="{}" '.format(key, value) for key, value in attrs.items())
        return '<input type="submit" class="btnSubmit" value="{0}" {1}/>'.format(value or 'Submit', attribs)

    @staticmethod
    def text(name, value='', type='text', attrs={}):
        """Returns markup for the text input element of name `name`, value `value`,
        and attributes `attrs`"""
        return Html.input(name, type, value=value, attrs=attrs)

def json_code_result(status_code, data=None):
    """Returns a `flask.Response` object with the given status code and data"""
    data = data or {}
    if isinstance(data, dict) and 'success' not in data:
        data['success'] = status_code >= 200 and status_code < 300
    return flask.jsonify(data), status_code

def print_request_args():
    """Prints the incoming request arguments data"""
    clay.text.pretty_print('Incoming request args data', flask.request.args)

def print_request_form():
    """Prints the incoming request form data"""
    clay.text.pretty_print('Incoming request form data', flask.request.form)

if __name__ == '__main__':

    from clay.tests import testif
    from clay.utils import qualify

    testif('raises TypeError for invalid string type',
        lambda: Html.get_newlines_string(None),
        None,
        raises=TypeError,
        name=qualify(Html.get_newlines_string))

    testif('accepts string of type bytes',
        Html.get_newlines_string(b''),
        b'',
        name=qualify(Html.get_newlines_string))

    html_get_newlines_string_tests = [
        (b'First line\r\nSecond line', b'First line<br />Second line'),
        ('First line\r\nSecond line', 'First line<br />Second line')
    ]

    for test in html_get_newlines_string_tests:
        testif('returns correct HTML newlines string when contains carriage return (type: {})'
                .format(type(test[0]).__name__),
            Html.get_newlines_string(test[0]),
            test[1],
            name=qualify(Html.get_newlines_string))

    testif('returns correct HTML newlines string',
        Html.get_newlines_string('First line\nSecond line'),
        'First line<br />Second line',
        name=qualify(Html.get_newlines_string))

    test_md_str_input = 'Test: Insert link <a target="_blank" href="http://www.comcast.net">here~^</a> [link2](http://www.google.com) and [link3](http://youtube.com)'
    test_md_str_output = 'Test: Insert link <a target="_blank" href="http://www.comcast.net">here~^</a> <a target="_blank" href="http://www.google.com">link2~^</a> and <a target="_blank" href="http://youtube.com">link3~^</a>'
    testif('replaces md links correctly',
        Html.replace_md_with_anchor(test_md_str_input),
        test_md_str_output,
        name=qualify(Html.replace_md_with_anchor))

    testif('returns correct HTML string',
        Html.input('tests', 'text'),
        '<input type="text" id="tests" name="tests" value="" />',
        name=qualify(Html.input))

    testif('returns correct HTML string (not checked)',
        Html.checkbox('hasTests'),
        '<input type="checkbox" id="hasTests" name="hasTests" value="" />',
        name=qualify(Html.checkbox))
    testif('returns correct HTML string (checked)',
        Html.checkbox('hasTests', checked=True),
        '<input type="checkbox" id="hasTests" name="hasTests" value="" checked="checked" />',
        name=qualify(Html.checkbox))

    testif('returns correct HTML string',
        Html.date('testDate', '2020-12-11'),
        '<input type="date" id="testDate" name="testDate" value="2020-12-11" />',
        name=qualify(Html.date))

    testif('returns correct HTML string',
        Html.hidden('testId', '01234'),
        '<input type="hidden" id="testId" name="testId" value="01234" />',
        name=qualify(Html.hidden))

    testif('returns correct HTML string (no value)',
        Html.submit(),
        '<input type="submit" class="btnSubmit" value="Submit" />',
        name=qualify(Html.submit))
    testif('returns correct HTML string (with value)',
        Html.submit('Save'),
        '<input type="submit" class="btnSubmit" value="Save" />',
        name=qualify(Html.submit))
    testif('returns correct HTML string (with attrs)',
        Html.submit(attrs={'id': 'btnSubmitChanges', 'style': 'display: none'}),
        '<input type="submit" class="btnSubmit" value="Submit" id="btnSubmitChanges" style="display: none" />',
        name=qualify(Html.submit))

    testif('returns correct HTML string',
        Html.text('testName'),
        '<input type="text" id="testName" name="testName" value="" />',
        name=qualify(Html.text))
