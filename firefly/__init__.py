from flask import Flask


def create_app(config=None):
    app = Flask(__name__)

    default_config = {
        "db": {"uri": "mongodb://localhost:27017", "name": "firefly"},
        "secret_key": "secret-code",
    }

    if config is not None:
        default_config.update(config)

    app.config.update(default_config)
    app.secret_key = default_config["secret_key"]

    from firefly import links, preferences, views, notes

    app.register_blueprint(links.bp)
    app.register_blueprint(preferences.bp)
    app.register_blueprint(views.bp)
    app.register_blueprint(notes.bp)
    app.add_url_rule("/", endpoint="links.links")

    @app.context_processor
    def inject_prefs():
        return {"prefs": preferences.get_preferences()}

    return app
