from flask import jsonify, request

from . import api
from .authentication import auth,verify_user
from .errors import bad_request, unauthorized


from ..models import User



@api.route('/users/<int:id>', methods = ['POST'])
#@auth.login_required
def get_user(id):
    if request.json is None:
        return bad_request("this api required json")

    user = verify_user(request.json)

    if user is None:
        return unauthorized('invalid username or password')

    user = User.query.get_or_404(id)

    if user is None: 
        return bad_request('user not found')

    return jsonify(user.to_json(),code=200)