
"""
Net metrics

"""

from clay.models import Serializable as _Serializable

class BarMetric(_Serializable):

    """Used to render HTML bar metrics to display progress visually"""

    def __init__(self, name='BarMetric', percent=0, color='#000000', direction=None):
        """
        Initializes this bar metric with the given name, percent (out of 100),
        color hash, and direction integer

        """
        self.name = name
        self.percent = percent
        self.color = color
        self.direction = direction

    @property
    def props(self):
        return {'name': str, 'percent': float, 'color': str, 'direction': int}

    def to_html(self, include_label=True):
        """Returns this bar metric with or without label as HTML for a view"""

        if include_label:
            if self.direction is not None:
                indicator = ' ' + ('(+)' if self.direction > 0
                    else '(0)' if self.direction == 0
                    else '(-)') # if self.direction < 0
            else:
                indicator = ''
            label = """<label for="{0}">{0} : {1}%{2}</label>""" \
                .format(self.name, self.percent, indicator)
        else:
            label = ''
        span = """<span id="{}" style="width: {}%; height: 7px; background-color: {};"></span>""" \
            .format(self.name, self.percent, self.color)

        return label + span

if __name__ == '__main__':

    from clay.tests import testif
    from clay.utils import qualify

    testif('converts bar to HTML correctly (defaults)',
        BarMetric().to_html(),
        '<label for="BarMetric">BarMetric : 0%</label>' + \
        '<span id="BarMetric" style="width: 0%; height: 7px; background-color: #000000;"></span>',
        name=qualify(BarMetric.to_html))

    testif('converts bar to HTML correctly (name)',
        BarMetric(name='Countdown').to_html(),
        '<label for="Countdown">Countdown : 0%</label>' + \
        '<span id="Countdown" style="width: 0%; height: 7px; background-color: #000000;"></span>',
        name=qualify(BarMetric.to_html))

    testif('converts bar to HTML correctly (percent)',
        BarMetric(percent=54.3).to_html(),
        '<label for="BarMetric">BarMetric : 54.3%</label>' + \
        '<span id="BarMetric" style="width: 54.3%; height: 7px; background-color: #000000;"></span>',
        name=qualify(BarMetric.to_html))

    color_tests = [
        (
            BarMetric(color='#aabbcc').to_html(),
            '<label for="BarMetric">BarMetric : 0%</label>' + \
            '<span id="BarMetric" style="width: 0%; height: 7px; background-color: #aabbcc;"></span>'
        ),
        (
            BarMetric(color='red').to_html(),
            '<label for="BarMetric">BarMetric : 0%</label>' + \
            '<span id="BarMetric" style="width: 0%; height: 7px; background-color: red;"></span>'
        )
    ]

    for color_test in color_tests:
        testif('converts bar to HTML correctly (color)',
            *color_test,
            name=qualify(BarMetric.to_html))

    direction_tests = [
        (
            BarMetric(direction=1).to_html(),
            '<label for="BarMetric">BarMetric : 0% (+)</label>' + \
            '<span id="BarMetric" style="width: 0%; height: 7px; background-color: #000000;"></span>'
        ),
        (
            BarMetric(direction=0).to_html(),
            '<label for="BarMetric">BarMetric : 0% (0)</label>' + \
            '<span id="BarMetric" style="width: 0%; height: 7px; background-color: #000000;"></span>'
        ),
        (
            BarMetric(direction=-1).to_html(),
            '<label for="BarMetric">BarMetric : 0% (-)</label>' + \
            '<span id="BarMetric" style="width: 0%; height: 7px; background-color: #000000;"></span>'
        )
    ]

    for direction_test in direction_tests:
        testif('converts bar to HTML correctly (direction)',
            *direction_test,
            name=qualify(BarMetric.to_html))
