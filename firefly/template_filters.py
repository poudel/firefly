import re
from jinja2 import evalcontextfilter, Markup, escape

_paragraph_re = re.compile(r"(?:\r\n|\r|\n){2,}")


@evalcontextfilter
def linebreaksbr(eval_ctx, value):
    """
    Convert a newline to <br>
    Source: http://jinja.pocoo.org/docs/2.10/api/#custom-filters
    """
    result = u"\n\n".join(
        u"<p>%s</p>" % p.replace("\n", Markup("<br>\n"))
        for p in _paragraph_re.split(escape(value))
    )
    if eval_ctx.autoescape:
        result = Markup(result)
    return result
