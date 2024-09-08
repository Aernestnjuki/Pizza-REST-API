from flask_restx import Namespace, Resource, fields
from ..models.orders_tb import Order
from ..models.users_tb import User
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils import db

orders_ns = Namespace('order', description="Namespace for Orders")

# Model that will be expected when we are changing something in the database
order_model = orders_ns.model(
    'Expected Order changes',
    {
        'id': fields.Integer(description='An ID'),
        'size': fields.String(
            description='Size of orders',
            required=True,
            enum=['SMALL', 'MEDIUM', 'LARGE', 'EXTRA_LARGE']
        ),
        'flavour': fields.String(required=True, description='Order flavour'),
        'quantity': fields.Integer(required=True, description='Number of pizza ordered by the client'),
    }
)

# model that will be used to marshal or return json data
all_order_model = orders_ns.model(
    "Get all orders",
{
        'id': fields.Integer(description='An ID'),
        'size': fields.String(
            description='Size of orders',
            required=True,
            enum=['SMALL', 'MEDIUM', 'LARGE', 'EXTRA_LARGE']
        ),
        'order_status': fields.String(
            description='Status of the order',
            required=True,
            enum=['PENDING', 'IN_TRANSIT', 'DELIVERED']
        ),
        'flavour': fields.String(required=True, description='Order flavour'),
        'quantity': fields.Integer(required=True, description='Number of pizza ordered by the client'),
        'user': fields.Integer(description='User Id that made the Order')
    }
)

#model to update the order status
order_status_model = orders_ns.model(
    "Order Status",
    {
        "order_status": fields.String(
            required=True,
            decription="Order status to update",
            enum=['PENDING', 'IN_TRANSIT', 'DELIVERED']
        )
    }
)

@orders_ns.route('/orders')
class OrderGetCreate(Resource):

    @orders_ns.marshal_with(all_order_model)
    @orders_ns.doc(description='Retrieve all orders')
    @jwt_required()
    def get(self):
        """Get all Orders"""

        orders = Order.query.all()
        return orders, HTTPStatus.OK

    @orders_ns.expect(order_model)
    @orders_ns.marshal_with(all_order_model)
    @orders_ns.doc(description="Place an order")
    @jwt_required()
    def post(self):
        """Create a new Order"""

        data = orders_ns.payload # user this instead of request.get_json()

        new_order = Order(
            size=data['size'],
            quantity=data['quantity'],
            flavour=data['flavour']
        )

        # the user stored in the jwt identity that was logged in
        username = get_jwt_identity()

        # getting the user how placed the Order
        current_user = User.query.filter_by(username=username).first()


        # getting and adding the user who created the order from the defined foreign key in the orders table
        new_order.customer = current_user

        new_order.save()

        return new_order, HTTPStatus.CREATED


@orders_ns.route('/order/<int:order_id>')
class GetUpdateDelete(Resource):

    @orders_ns.marshal_with(all_order_model)
    @orders_ns.doc(description="Retrieves an order by its ID", params={"order_id": "An ID for a given order"})
    @jwt_required()
    def get(self, order_id):
        """Retrieve an Order by ID"""
        order = Order.get_by_id(order_id)

        return order, HTTPStatus.OK

    @orders_ns.expect(order_model)
    @orders_ns.marshal_with(all_order_model)
    @orders_ns.doc(description="Updates an order by it ID", params={"order_id": "An ID for a given order"})
    @jwt_required()
    def put(self, order_id):
        """Update an Order by ID"""

        order_to_update = Order.get_by_id(order_id)

        data = orders_ns.payload

        order_to_update.quantity = data['quantity']
        order_to_update.size = data['size']
        order_to_update.flavour = data['flavour']

        db.session.commit()

        return order_to_update, HTTPStatus.OK

    @orders_ns.marshal_with(all_order_model)
    @orders_ns.doc(description="Deletes and order by it ID", params={"order_id": "An ID for a given order"})
    @jwt_required()
    def delete(self, order_id):
        """Delete an Order by ID"""

        order_to_delete = Order.get_by_id(order_id)

        order_to_delete.deleted()

        return order_to_delete, HTTPStatus.NO_CONTENT


# there is an error here with the sql query
@orders_ns.route('/user/<int:user_id>/order/<int:order_id>')
class getSpecificOrderByUser(Resource):

    @orders_ns.marshal_with(all_order_model)
    @orders_ns.doc(description="Gets user specific orders",
                   params={"order_id": "An ID for a given order",
                           "user_id": "A Users ID"
                           })
    @jwt_required()
    def get(self, user_id, order_id):
        """Retrieve specific user id by order id"""

        user = User.get_by_id(user_id)

        order = Order.query.filter_by(id=order_id).filter_by(customer=user).first()

        return order, HTTPStatus.OK




@orders_ns.route('/user/<int:user_id>/orders')
class UserOrders(Resource):

    @orders_ns.marshal_list_with(all_order_model)
    @orders_ns.doc(description="Get orders of a user given an order ID", params={"user_id": "A user's ID"})
    def get(self, user_id):
        """Get all orders by a specific user"""

        user = User.get_by_id(user_id)

        # get a list of orders attached to this user
        orders = user.orders

        return orders, HTTPStatus.OK


@orders_ns.route('/order/status/<int:order_id>')
class UpdateOrderStatus(Resource):

    @orders_ns.expect(order_status_model)
    @orders_ns.marshal_with(all_order_model)
    @orders_ns.doc(description="Update an order status give the order ID", params={"order_id": "An ID for a given order"})
    @jwt_required()
    def patch(self, order_id):
        """Update and order's status"""

        data = orders_ns.payload

        order_status_update = Order.get_by_id(order_id)

        order_status_update.order_status = data['order_status']

        db.session.commit()

        return order_status_update, HTTPStatus.OK