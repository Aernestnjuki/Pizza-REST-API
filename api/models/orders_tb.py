from ..utils import db
from enum import Enum
from _datetime import datetime

# class to create pizza size choices in the database
class Sizes(Enum):
    SMALL = 'small',
    MEDIUM = 'medium',
    LARGE = 'large',
    EXTRA_LARGE = 'extra_large'

# class to create order_status choices in the database
class OrderStatus(Enum):
    PENDING = 'pending'
    IN_TRANSIT = 'in_transit'
    DELIVERED = 'delivered'


# database model
class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer(), primary_key=True)
    size = db.Column(db.Enum(Sizes), default = Sizes.SMALL)
    order_status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING)
    flavour = db.Column(db.String(), nullable=False)
    quantity = db.Column(db.Integer())
    user = db.Column(db.Integer(), db.ForeignKey('users.id')) # foreign key references the table
    date_created = db.Column(db.DateTime(), default=datetime.utcnow)


    def __repr__(self):
        return f'<Order {self.id}>'

    def save(self):
        db.session.add(self)
        db.session.commit()

    def deleted(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)