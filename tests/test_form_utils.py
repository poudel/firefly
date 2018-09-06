import pytest
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, IntegerField
from wtforms.fields.core import UnboundField
from firefly.form_utils import (
    get_form_fields,
    get_default_from_fields,
    get_form_defaults,
)


@pytest.fixture
def form_class():
    class MyForm(FlaskForm):
        field_yes = BooleanField("field yes", default=True)
        field_str = StringField("field str", default="asdf")
        field_num = IntegerField("field num", default=100)

    return MyForm


def test_get_form_fields(form_class):
    fields = get_form_fields(form_class)

    assert len(fields) == 3
    assert isinstance(fields, dict)

    for field in fields.values():
        assert isinstance(field, UnboundField)


def test_get_default_config_from_fields(form_class):
    fields = get_form_fields(form_class)
    defaults = get_default_from_fields(fields)

    assert defaults["field_yes"] == True
    assert defaults["field_str"] == "asdf"
    assert defaults["field_num"] == 100


def test_get_form_defaults(form_class):
    defaults = get_form_defaults(form_class)

    assert defaults["field_yes"] == True
    assert defaults["field_str"] == "asdf"
    assert defaults["field_num"] == 100
