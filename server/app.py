# server/app.py
import os
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from models import db, Restaurant, Pizza, RestaurantPizza

def create_app():
    app = Flask(__name__)
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db)

    # Create tables if they don’t exist
    with app.app_context():
        db.create_all()

    @app.route('/')
    def home():
        return jsonify({"message": "Pizza API"})

    @app.route('/restaurants', methods=['GET'])
    def get_restaurants():
        restaurants = Restaurant.query.all()
        return jsonify([r.to_dict() for r in restaurants]), 200

    @app.route('/restaurants/<int:id>', methods=['GET'])
    def get_restaurant(id):
        r = Restaurant.query.get(id)
        if not r:
            return jsonify({"error": "Restaurant not found"}), 404
        return jsonify(r.to_dict_with_pizzas()), 200

    @app.route('/restaurants/<int:id>', methods=['DELETE'])
    def delete_restaurant(id):
        r = Restaurant.query.get(id)
        if not r:
            return jsonify({"error": "Restaurant not found"}), 404
        db.session.delete(r)
        db.session.commit()
        return ("", 204)

    @app.route('/pizzas', methods=['GET'])
    def get_pizzas():
        pizzas = Pizza.query.all()
        return jsonify([p.to_dict() for p in pizzas]), 200

    @app.route('/restaurant_pizzas', methods=['POST'])
    def create_restaurant_pizza():
        data = request.get_json() or {}
        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        # Basic required fields check
        errors = []
        if price is None:
            errors.append("Price is required")
        if pizza_id is None:
            errors.append("pizza_id is required")
        if restaurant_id is None:
            errors.append("restaurant_id is required")
        if errors:
            return jsonify({"errors": errors}), 422

        # existence checks
        pizza = Pizza.query.get(pizza_id)
        if not pizza:
            return jsonify({"errors": ["Pizza not found"]}), 404
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            return jsonify({"errors": ["Restaurant not found"]}), 404

        # Validate price is integer and within range
        try:
            price_int = int(price)
        except (TypeError, ValueError):
            return jsonify({"errors": ["Price must be an integer"]}), 422

        if price_int < 1 or price_int > 30:
            return jsonify({"errors": ["Price must be between 1 and 30"]}), 422

        rp = RestaurantPizza(price=price_int, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(rp)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"errors": [str(e)]}), 422

        rp = RestaurantPizza.query.get(rp.id)
        return jsonify(rp.to_dict_with_restaurant_and_pizza()), 201

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=5555, debug=True)
