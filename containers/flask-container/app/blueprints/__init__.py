from flask import Blueprint

def init_app(app):
    from .user_api import user_api
    from .spark_api import spark_api

    app.register_blueprint(user_api)
    app.register_blueprint(spark_api)
