import unittest
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from werkzeug.security import generate_password_hash
from ..models.users_tb import User


# remember to install pyTest

class UserTestCase(unittest.TestCase):

    # set up function create a database and a client in the memory
    def setUp(self):
        self.app = create_app(config=config_dict['test'])

        self.appctx = self.app.app_context()

        self.appctx.push()

        # create a test client that will be used to test the api
        self.client = self.app.test_client()

        db.create_all()

    # tear down function destroys the created database when the test stops running
    def tearDown(self):

        db.drop_all()

        self.appctx.pop()

        self.app = None

        self.client = None


    # Test 1: testing the SignUp route in the auth
    def test_user_registration(self):

        data = {
            "username": "testuser",
            "email": "testuser@user.com",
            "password": "password"
        }
        response = self.client.post('/auth/signup', json=data)

        # checking if the user exits
        user = User.query.filter_by(email='testuser@user.com').first()


        assert user.username == 'testuser'

        assert response.status_code == 201

    # Test 2: Login
    def test_login(self):
        data = {
            "email": "testuser@user.com",
            "password": "password"
        }

        response = self.client.post('/auth/login', json=data)

        assert response.status_code == 400

        # note that here we expect to get a 400 response as the database is empty
        # if it was not empty, we could have returned a 200 OK response

