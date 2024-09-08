import unittest
from .. import create_app
from ..config.config import config_dict
from ..models.orders_tb import Order
from ..utils import db
from flask_jwt_extended import create_access_token

class OrderTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config=config_dict['test'])

        self.appctx = self.app.app_context()

        self.appctx.push()
        self.client = self.app.test_client()

        db.create_all()

    def tearDown(self):
        db.drop_all()

        self.app = None
        self.appctx.pop()
        self.client = None

    # Test 3: Get all orders
    def test_get_all_orders(self):

        token = create_access_token(identity='testuser')

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = self.client.get('/orders/orders', headers=headers) # get is the method we used

        # here we expect to get an empty list as there is nothing in the database

        assert response.status_code == 200

        assert response.json == []

    # Test 4: Creating an order
    def test_create_order(self):

        data = {
            "size": "LARGE",
            "quantity": 2,
            "flavour": "chicken"
        }

        token = create_access_token(identity='testuser')

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = self.client.post('/orders/orders', json=data, headers=headers) # post is the method to create orders

        assert response.status_code == 201

        order = Order.query.all()

        assert len(order) == 1