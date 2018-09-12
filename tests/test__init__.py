from firefly import create_app


def test_create_app_testing_config():
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_create_app_registers_blueprints():
    app = create_app()
    assert len(app.blueprints) == 5
    assert app.blueprints["links"]
    assert app.blueprints["preferences"]
    assert app.blueprints["views"]
    assert app.blueprints["notes"]
    assert app.blueprints["archive"]


def test_create_app_override_config():
    app = create_app({"secret_key": "RANXOM"})
    assert app.config["secret_key"] == "RANXOM"
