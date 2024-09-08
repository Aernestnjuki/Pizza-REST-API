from flask import Flask
from flask_restx import Api
from .auth.views import auth_ns
from .orders.views import orders_ns
from .config.config import config_dict
from .utils import db
from .models.orders_tb import Order
from .models.users_tb import User
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import NotFound, MethodNotAllowed


def create_app(config=config_dict['dev']):
    app = Flask(__name__)

    app.config.from_object(config)

    db.init_app(app)

    jwt = JWTManager(app)

    # set up flask-migrate
    migrate = Migrate(app, db)


    # allowing the users to add an Authorization key to tye swagger ui
    authorizations = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Add a JWT with ** Bearer &lt;JWT&gt;  to authorize"
        }
    }

    api = Api(
        app,
        title='Pizza Rest API',
        description='An API that handles pizza orders and deliveries',
        authorizations=authorizations,
        security="Bearer Auth"
    )

    # register the namespaces
    api.add_namespace(orders_ns, path='/orders')
    api.add_namespace(auth_ns, path='/auth')

    # these are functions that will handle some exceptions that the browser throws at as
    # 1. NotFound error
    @api.errorhandler(NotFound)
    def not_found(error):
        return {"error": "Not Found"}, 404

    # 2. Not Allowed
    @api.errorhandler(MethodNotAllowed)
    def method_not_allowed(error):
        return {"error": "Method Not Allowed"}, 405

    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'user': User,
            'order': Order
        }


    return app