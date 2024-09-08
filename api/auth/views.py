from flask_restx import Namespace, Resource, fields
from flask import request
from ..models.users_tb import User
from werkzeug.security import generate_password_hash, check_password_hash
from http import HTTPStatus
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.exceptions import Conflict, BadRequest

auth_ns = Namespace('auth', description="Namespace for authentication")


# this model will be required to sign up
signup_model = auth_ns.model(
    'SignUp User',
    {
        'id': fields.Integer(),
        'username': fields.String(required=True, description='A username'),
        'email': fields.String(required=True, description='An email'),
        'password': fields.String(required=True, description='A password')
    }
)

# this model with be used to marshal or to return a json response
get_user_model = auth_ns.model(
    'Get User',
    {
        'id': fields.Integer(),
        'username': fields.String(required=True, description='A username'),
        'email': fields.String(required=True, description='An email'),
        'password_hash': fields.String(required=True, description='A password'),
        'is_active': fields.Boolean(description='Shows user is active'),
        'is_staff': fields.Boolean(description='Shows user is a staff')
    }
)

login_model = auth_ns.model(
    'Login',
    {
        'email': fields.String(required=True, description='An email'),
        'password': fields.String(required=True, description='A password')
    }
)



@auth_ns.route('/signup')
class SignUp(Resource):

    @auth_ns.expect(signup_model)
    @auth_ns.marshal_with(get_user_model) # this will help return a json response using the signup_model
    def post(self):
        """Sign Up a new Account"""

        data = request.get_json()

        try:

            new_user = User(
                username = data.get('username'),
                email = data.get('email'),
                password_hash = generate_password_hash(data.get('password'))
            )

            new_user.save()

            return new_user, HTTPStatus.CREATED
        except Exception as e:
            raise Conflict(f"User with username {data.get('username')} or email {data.get('email')} already exists")


@auth_ns.route('/login')
class Login(Resource):

    @auth_ns.expect(login_model)
    def post(self):
        """Login and generate JWT Tokens"""

        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=user.username)
            refresh_token = create_refresh_token(identity=user.username)

            response = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }

            return response, HTTPStatus.OK
        raise BadRequest("Invalid Username or Password")

@auth_ns.route('/refresh')
class Refresh(Resource):

    @jwt_required(refresh=True)
    def post(self):
        """Creating a new refresh token to update the access token"""

        username = get_jwt_identity()

        access_token = create_access_token(identity=username)

        return {"access_token": access_token}, HTTPStatus.OK