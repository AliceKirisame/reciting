import json
from flask import jsonify, request

from . import api
from .authentication import auth
from .errors import bad_request
from .authentication import verify_user

from ..models import Order, OrderDetail, Food
from .. import db

#e_mail, password, count, 0,1,...,count
@api.route('/order', methods = ['POST'])
#@auth.login_required
def ordering():
    if request.json is None:
        return bad_request("this api requires json")
    user = verify_user(request.json)

    if user is None:
        return unauthorized('invalid username or password')

    order,details = Order.from_json(request.json)
    totalPrice = 0

    db.session.add(order)

    for detail in details:

        food_id = int(detail["id"])
        food_count = int(detail["count"])

        if food_id is None or food_id < 0:
            return bad_request('food num error occurred')

        if food_count is None or food_count < 0:
            return bad_request('food num error occurred')

        food = Food.query.filter_by(id=food_id).first()

        if food is None:
            return bad_request('illegal order')

        totalPrice += food.price * food_count

        od = OrderDetail.from_json({'food_id':food_id, 'order_id':order})

        db.session.add(od)

    db.session.commit()

    return jsonify({'code':200, 'id':order.id, 'price':str(totalPrice)})

@api.route('/foods', methods = ['GET'])
def foods():
    #return jsonify(Food.to_json())
    return json.dumps(Food.to_json(), ensure_ascii=False)