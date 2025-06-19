#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

# GET all bakeries
@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(bakeries, 200)

# GET one bakery by id
@app.route('/bakeries/<int:id>')
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()
    if not bakery:
        return make_response({"error": "Bakery not found"}, 404)
    return make_response(bakery.to_dict(), 200)

# PATCH bakery name
@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    bakery = Bakery.query.get(id)
    if not bakery:
        return make_response({"error": "Bakery not found"}, 404)

    name = request.form.get("name")
    if name:
        bakery.name = name
        db.session.commit()
        return make_response(bakery.to_dict(), 200)
    
    return make_response({"error": "No name provided"}, 400)

# GET baked goods sorted by price (desc)
@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    goods = BakedGood.query.order_by(BakedGood.price.desc()).all()
    return make_response([bg.to_dict() for bg in goods], 200)

# GET the most expensive baked good
@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).first()
    if not most_expensive:
        return make_response({"error": "No baked goods found"}, 404)
    return make_response(most_expensive.to_dict(), 200)

# POST new baked good
@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    name = request.form.get("name")
    price = request.form.get("price")
    bakery_id = request.form.get("bakery_id")

    if not all([name, price, bakery_id]):
        return make_response({"error": "Missing form data"}, 400)

    try:
        new_bg = BakedGood(name=name, price=float(price), bakery_id=int(bakery_id))
        db.session.add(new_bg)
        db.session.commit()
        return make_response(new_bg.to_dict(), 201)
    except Exception as e:
        return make_response({"error": str(e)}, 500)

# DELETE baked good by id
@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    bg = BakedGood.query.get(id)
    if not bg:
        return make_response({"error": "Baked good not found"}, 404)

    db.session.delete(bg)
    db.session.commit()
    return make_response({"message": "Baked good deleted successfully"}, 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
