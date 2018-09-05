from flask import Flask


def create_app(config=None):
    app = Flask(__name__)

    default_config = {"db": {"uri": "mongodb://localhost:27017", "name": "firefly"}}
    if config is not None:
        default_config.update(config)
    app.config.update(default_config)

    from firefly import links

    app.register_blueprint(links.bp)
    app.add_url_rule("/", endpoint="links.links")
    return app
