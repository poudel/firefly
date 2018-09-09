import pytest
from jinja2 import Markup
from firefly.template_filters import linebreaksbr


@pytest.fixture
def ctx():
    class Ctx:
        autoescape = False

    return Ctx


def test_linebreaksbr(ctx):
    result = linebreaksbr(ctx, "I am \n")
    assert result == "<p>I am <br>\n</p>", "Should replace nl with br"
    assert result.startswith("<p>") and result.endswith(
        "</p>"
    ), "Should wrap everything in <p> tag"

    text = "Hello\n\nworld"
    assert (
        linebreaksbr(ctx, text) == "<p>Hello</p>\n\n<p>world</p>"
    ), "Should wrap texts separated by two newlines by <p> tags"


def test_linebreaksbr_return_value(ctx):
    ctx.autoescape = False
    assert not isinstance(linebreaksbr(ctx, "I am \n"), Markup)
    assert isinstance(linebreaksbr(ctx, "I am \n"), str)

    ctx.autoescape = True
    assert isinstance(linebreaksbr(ctx, "I am \n"), Markup)
