import uuid
from datetime import datetime
from sqlalchemy.dialects.mysql import DECIMAL

from . import db, bcrypt

def generate_uuid():
    return str(uuid.uuid4())

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    cart = db.relationship('Cart', back_populates='user', uselist=False, cascade="all, delete-orphan")
    orders = db.relationship('Order', back_populates='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(DECIMAL(precision=10, scale=2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    image_url = db.Column(db.String(255), nullable=True)
    cart_items = db.relationship('CartItem', back_populates='product', lazy=True)
    order_items = db.relationship('OrderItem', back_populates='product', lazy=True)

    def __repr__(self):
        return f"<Product {self.name}>"

class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='cart')
    items = db.relationship('CartItem', back_populates='cart', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cart {self.id} for User {self.user_id}>"

class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    cart_id = db.Column(db.String(36), db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    __table_args__ = (db.UniqueConstraint('cart_id', 'product_id', name='_cart_product_uc'),)

    cart = db.relationship('Cart', back_populates='items')
    product = db.relationship('Product', back_populates='cart_items')

    def __repr__(self):
        return f"<CartItem Product {self.product_id} Qty {self.quantity} in Cart {self.cart_id}>"


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    total_price = db.Column(DECIMAL(precision=10, scale=2), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    shipped_at = db.Column(db.DateTime, nullable=True)
    shipping_address = db.Column(db.Text, nullable=True)
    billing_address = db.Column(db.Text, nullable=True)
    payment_gateway_ref = db.Column(db.String(255), nullable=True)

    user = db.relationship('User', back_populates='orders')
    items = db.relationship('OrderItem', back_populates='order', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order {self.id} Status {self.status} by User {self.user_id}>"

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(DECIMAL(precision=10, scale=2), nullable=False)

    order = db.relationship('Order', back_populates='items')
    product = db.relationship('Product', back_populates='order_items')

    def __repr__(self):
        return f"<OrderItem Product {self.product_id} Qty {self.quantity} Price {self.price_at_purchase} in Order {self.order_id}>"