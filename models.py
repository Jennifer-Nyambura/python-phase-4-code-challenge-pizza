# server/models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()

class Restaurant(db.Model):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    # a restaurant has many restaurant_pizzas (cascade deletes)
    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        back_populates="restaurant",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address
        }

    def to_dict_with_pizzas(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "restaurant_pizzas": [rp.to_dict_with_pizza() for rp in self.restaurant_pizzas]
        }

class Pizza(db.Model):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        back_populates="pizza",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "ingredients": self.ingredients
        }

class RestaurantPizza(db.Model):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)

    pizza = db.relationship("Pizza", back_populates="restaurant_pizzas")
    restaurant = db.relationship("Restaurant", back_populates="restaurant_pizzas")

    @validates('price')
    def validate_price(self, key, value):
        # ensure integer-like
        if value is None:
            raise ValueError("Price must be provided")
        try:
            v = int(value)
        except (TypeError, ValueError):
            raise ValueError("Price must be an integer")
        if v < 1 or v > 30:
            raise ValueError("Price must be between 1 and 30")
        return v

    def to_dict(self):
        return {
            "id": self.id,
            "price": self.price,
            "pizza_id": self.pizza_id,
            "restaurant_id": self.restaurant_id
        }

    def to_dict_with_pizza(self):
        return {
            "id": self.id,
            "pizza": self.pizza.to_dict(),
            "pizza_id": self.pizza_id,
            "price": self.price,
            "restaurant_id": self.restaurant_id
        }

    def to_dict_with_restaurant_and_pizza(self):
        return {
            "id": self.id,
            "pizza": self.pizza.to_dict(),
            "pizza_id": self.pizza_id,
            "price": self.price,
            "restaurant": self.restaurant.to_dict(),
            "restaurant_id": self.restaurant_id
        }
