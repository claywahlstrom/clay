
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

def json_code_result(status_code, message=''):
    """Returns a `flask.Response` object with the given status code and message"""
    return flask.jsonify(hasMessage=bool(message),
        message=message,
        status_code=status_code,
        success=status_code >= 200 and status_code < 300), status_code

def print_request_args():
    """Prints the incoming request arguments data"""
    clay.text.pretty_print('Incoming request args data', flask.request.args)

def print_request_form():
    """Prints the incoming request form data"""
    clay.text.pretty_print('Incoming request form data', flask.request.form)

if __name__ == '__main__':

    from clay.tests import testif
    from clay.utils import qualify

    testif('Raises TypeError for invalid string type',
        lambda: Html.get_newlines_string(None),
        None,
        raises=TypeError,
        name=qualify(Html.get_newlines_string))

    testif('Accepts string of type bytes',
        Html.get_newlines_string(b''),
        b'',
        name=qualify(Html.get_newlines_string))

    html_get_newlines_string_tests = [
        (b'First line\r\nSecond line', b'First line<br />Second line'),
        ('First line\r\nSecond line', 'First line<br />Second line')
    ]

    for test in html_get_newlines_string_tests:
        testif('Returns correct HTML newlines string when contains carriage return (type: {})'
                .format(type(test[0]).__name__),
            Html.get_newlines_string(test[0]),
            test[1],
            name=qualify(Html.get_newlines_string))

    testif('Returns correct HTML newlines string',
        Html.get_newlines_string('First line\nSecond line'),
        'First line<br />Second line',
        name=qualify(Html.get_newlines_string))

    test_md_str_input = 'Test: Insert link <a target="_blank" href="http://www.comcast.net">here~^</a> [link2](http://www.google.com) and [link3](http://youtube.com)'
    test_md_str_output = 'Test: Insert link <a target="_blank" href="http://www.comcast.net">here~^</a> <a target="_blank" href="http://www.google.com">link2~^</a> and <a target="_blank" href="http://youtube.com">link3~^</a>'
    testif('Replaces md links correctly',
        Html.replace_md_with_anchor(test_md_str_input),
        test_md_str_output,
        name=qualify(Html.replace_md_with_anchor))
