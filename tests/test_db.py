import mongomock
from pymongo import MongoClient, database
from flask import g
from firefly import create_app
from firefly.db import get_connection, get_db


def test_get_connection_while_not_testing():
    app = create_app({"TESTING": False})

    with app.app_context():
        assert not hasattr(g, "connection")
        connection = get_connection()
        assert hasattr(g, "connection")
        assert isinstance(connection, MongoClient)


def test_get_connection_while_testing():
    app = create_app({"TESTING": True})

    with app.app_context():
        assert not hasattr(g, "connection")
        connection = get_connection()
        assert hasattr(g, "connection")
        assert isinstance(connection, mongomock.MongoClient)


def test_get_db_while_not_testing(app):
    app = create_app({"TESTING": False})

    with app.app_context():
        db = get_db()
        assert hasattr(db, "name")
        assert isinstance(db, database.Database)


def test_get_db_while_testing(app):
    app = create_app({"TESTING": True})

    with app.app_context():
        db = get_db()
        assert hasattr(db, "name")
        assert isinstance(db, mongomock.database.Database)
