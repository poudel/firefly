import pytest
from flask_wtf import FlaskForm
from firefly.form_fields import TagListField


@pytest.fixture
def formclass(app):
    class Form(FlaskForm):
        tags = TagListField()

    return Form


@pytest.fixture
def request_ctx(app):
    ctx = app.test_request_context()
    ctx.push()

    yield ctx

    ctx.pop()


def test_TagListField__init__(request_ctx):
    class Form(FlaskForm):
        tags = TagListField(remove_duplicates=False, delimiter=",")

    form = Form()
    assert getattr(form.tags, "remove_duplicates") == False
    assert getattr(form.tags, "delimiter") == ","


def test_TagListField_removes_duplicates(formclass, request_ctx):
    form = formclass(data={"tags": "my my my link link link"})
    form.validate()
