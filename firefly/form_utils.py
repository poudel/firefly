from wtforms.fields.core import UnboundField


def get_form_fields(form_class):
    """
    Extract fields from a FlaskForm class and return them as a dict
    """
    form_fields = {}
    for attr_name in dir(form_class):
        attribute = getattr(form_class, attr_name)

        if isinstance(attribute, UnboundField):
            form_fields[attr_name] = attribute
    return form_fields


def get_default_from_fields(form_fields):
    """
    Takes a dictionary of field name and UnboundField instance
    and returns their default values as dict of field name and value
    """
    defaults = {}
    for field_name, field in form_fields.items():
        defaults[field_name] = field.kwargs["default"]
    return defaults


def get_form_defaults(form_class):
    """
    Takes a FlaskForm subclass and returns a map of field name and
    their default value
    """
    fields = get_form_fields(form_class)
    return get_default_from_fields(fields)
