import hashlib, time, copy

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from flask import g, jsonify, request, make_response
from flask_httpauth import HTTPBasicAuth

from .errors import unauthorized, forbidden, bad_request
from . import api
from . import wxmsg

from app.exceptions import ValidationError

from ..models import User
from .. import db

auth = HTTPBasicAuth()
token = 'eatwhat'

@auth.verify_password
def verify_password(e_mail, password):
    
    user = User.query.filter_by(e_mail = e_mail).first()

    if not user:
        return False

    g.current_user = user
    g.token_used = False

    return user.verify_password(password)

def verify_user(json_user):

    json_user["e_mail"]="a@a.com"
    json_user["password"]="a"


    e_mail = json_user.get('e_mail')
    if e_mail is None or e_mail == '':
        raise ValidationError('User does not have a e_mail')

    password = json_user.get('password')
    if password is None or password == '':
        raise ValidationError('User does not have a password')

    user = User.query.filter_by(e_mail = e_mail).first()

    if user is None:
        return None

    if not user.verify_password(password):
        return None

    g.current_user = user
    g.token_used = False

    return user

def test_json(json):
    if request.json is None:
        return False
    else:
        return True

@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')

@api.route('/', methods = ['GET', 'POST'])
def weChatAuth():
    if request.method == 'GET':
        query = request.args

        signature = query.get('signature')
        if signature is None:
            return bad_request('signature is required')

        timestamp = query.get('timestamp')
        if timestamp is None:
            return bad_request('timestamp is required')

        nonce = query.get('nonce')
        if nonce is None:
            return bad_request('nonce is required')

        echostr = query.get('echostr')
        if echostr is None:
            return bad_request('echostr is required')

        s = [timestamp, nonce, token]
        s.sort();

        s = ''.join(s)

        
        if(hashlib.sha1(s.encode('utf-8')).hexdigest() == signature):
            return make_response(echostr)

        return bad_request('signatrue is unmatched')

    

    recv_msg = wxmsg.GetMsgFromRequest()

    if(recv_msg is not None):

        if recv_msg.MsgType == 'text':
            
            reply_msg = wxmsg.ReplyTextMsg(recv_msg)

        elif recv_msg.MsgType == 'event':

            reply_msg = wxmsg.ReplyEventMsg(recv_msg)


        if isinstance(reply_msg, wxmsg.Msg):

            return wxmsg.MakeResponseFromMsg(reply_msg)

        else:
            return reply_msg


    return 'success'

#username, e_mail, password
@api.route('/register', methods = ['POST'])
def register():
    if request.json is None:
        return bad_request("this api requires json")

    user = User.from_json(request.json)

    db.session.add(user)
    db.session.commit()

    return jsonify({'code':200,' id':user.id, 'username':user.username})

#e_mail, password
@api.route('/login', methods = ['POST'])
#@auth.login_required
def login():
    if request.json is None:
        return bad_request("this api requires json")

    json_user = request.json

    user = verify_user(json_user)
    if user is None:
        return unauthorized('invalid username or password')

    return jsonify(user.to_json(),code=200)

#@api.before_request
#@auth.login_required
#def before_request():
#    pass