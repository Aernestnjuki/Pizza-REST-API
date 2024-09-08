from ..utils import db
from _datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True) # this will be a foreign key in the orders table
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.Text(), nullable=False)
    is_staff = db.Column(db.Boolean(), default=False)
    is_active = db.Column(db.Boolean(), default=False)

    # backref states how we are going the get the user
    orders = db.relationship('Order', backref='customer', lazy=True)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)