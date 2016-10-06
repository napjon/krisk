from krisk.util import join_current_dir


def save_html(script, path):

    from jinja2 import Template

    html_template = open(join_current_dir('static/template.html'), 'r')
    script = script.replace('element', '$("body")')
    f = open(path, 'w')
    f.write(Template(html_template.read()).render(SCRIPT=script))
    f.close()
    html_template.close()


APPEND_ELEMENT = """
$('#{id}').attr('id','{id}'+'_old');
element.append('<div id="{id}" style="width: {width}px;height:{height}px;"></div>');"""

OPTION_TEMPLATE = {
    'title': {
        'text': ''
    },
    'tooltip': {'axisPointer': {'type': ''}},
    'legend': {
        'data': []
    },
    'xAxis': {
        'data': []
    },
    'yAxis': {},
    'series': []
}
