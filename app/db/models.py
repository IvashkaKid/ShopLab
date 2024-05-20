from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class Style(Base):
    __tablename__ = 'style'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Set(Base):
    __tablename__ = 'sets'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    discount = Column(Integer, nullable=False)


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    style_id = Column(Integer, ForeignKey('style.id'))
    category = relationship("Category", backref="products")
    style = relationship("Style", backref="products")


class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)


class SetItem(Base):
    __tablename__ = 'set_items'
    id = Column(Integer, primary_key=True)
    set_id = Column(Integer, ForeignKey('sets.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    role = relationship("Role", backref="users")
    __table_args__ = (CheckConstraint('role_id IN (1, 2)', name='valid_role'),)


class SetOrder(Base):
    __tablename__ = 'set_order'
    id = Column(Integer, primary_key=True)
    set_id = Column(Integer, ForeignKey('sets.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    quantity = Column(Integer, nullable=False)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total_price = Column(Float)
    order_date = Column(DateTime, nullable=False, default=datetime.utcnow())
    user = relationship("User", backref="orders")
