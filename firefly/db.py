"""
Mongodb database functions.
"""
import mongomock
from pymongo import MongoClient
from flask import g, current_app


def get_connection():
    """
    Return a mongodb connection. It stores the connection inside the `g` object.
    """
    if "connection" not in g:
        if current_app.config["TESTING"]:
            g.connection = mongomock.MongoClient()
        else:
            g.connection = MongoClient(current_app.config["db"]["uri"])
    return g.connection


def get_db(name=None):
    """
    Return the mongodb database for the provided `name`.
    """
    name = name or current_app.config["db"]["name"]
    return get_connection()[name]
