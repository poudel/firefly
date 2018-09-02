from flask import Flask


def create_app(config=None):
    app = Flask(__name__)

    from firefly import links

    app.register_blueprint(links.bp)
    app.add_url_rule("/", endpoint="links.links")
    return app
