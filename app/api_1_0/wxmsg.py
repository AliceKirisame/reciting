import xml.etree.cElementTree as ET
import time
import re

from flask import request, make_response

from . import talktoe

from .. import db
from ..models import User, Food, Order, OrderDetail

def getFoodNumList(s):

	fo = r'^\#\(((?:\d{1,9}\,)*)(\d{1,9})\)$'

	m  = re.match(fo, s)

	if m is not None :
		gs = m.groups()
		head = gs[0]
		tail = gs[1]
		nowNum = ''
		numList = []

		for c in head:
			if c != ',':
				nowNum += c
			else:
				numList.append(int(nowNum))
				nowNum = ''

		numList.append(int(tail))

		return numList
	
	else:
		return None

class Msg(object):

    def __init__(self, xmlData=None,ToUserName=None, FromUserName=None, MsgType=None):

        if xmlData != None:

            self.ToUserName = xmlData.find('ToUserName').text
            self.FromUserName = xmlData.find('FromUserName').text
            self.MsgType = xmlData.find('MsgType').text
            self.CreateTime = xmlData. find('CreateTime').text
            if self.MsgType != 'event':
                self.MsgId = xmlData.find('MsgId').text
        else:
            self.ToUserName = ToUserName
            self.FromUserName = FromUserName
            self.MsgType = MsgType
            self.CreateTime = (str(int(time.time())))

class TextMsg(Msg):

    def __init__(self, xmlData=None,ToUserName=None, FromUserName=None, Content=None):
        
        Msg.__init__(self, xmlData, ToUserName, FromUserName, 'text')

        if xmlData != None:
            self.Content = xmlData.find('Content').text
        
        else:
            self.Content = Content

class EventMsg(Msg):

    def __init__(self, xmlData=None,ToUserName=None, FromUserName=None, Event=None):
        
        Msg.__init__(self, xmlData, ToUserName, FromUserName, 'event')

        if xmlData != None:
            self.Event = xmlData.find('Event').text
        
        else:
            self.Event = Event


class ImgMsg(Msg):

    def __init__(self, xmlData=None,ToUserName=None, FromUserName=None,  MediaId=None):
        
        Msg.__init__(self, xmlData, ToUserName, FromUserName, 'image')
        
        if xmlData != None:
            self.PicUrl = xmlData.find('PicUrl').text
            self.MediaId = xmlData.find('MediaId').text

        else:
            self.MediaId = MediaId


def DefaultReply(ToUserName,FromUserName):

    return TextMsg(None, ToUserName, FromUserName, '未识别消息类型')

def GetMsgFromRequest():

    xmlData = ET.fromstring(request.data)

    if(xmlData.find('MsgType').text == 'text'):
        return TextMsg(xmlData=xmlData)

    if(xmlData.find('MsgType').text == 'image'):
        return ImgMsg(xmlData=xmlData)

    if(xmlData.find('MsgType').text == 'event'):
        return EventMsg(xmlData=xmlData)

    else:
        return Msg(xmlData)

def MakeResponseFromMsg(Msg):

    ToUserName = Msg.ToUserName
    FromUserName = Msg.FromUserName
    MsgType = Msg.MsgType
    CreateTime = Msg.CreateTime

    if(MsgType == 'text'):

        Content = Msg.Content

        reply = '''<xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%s</CreateTime>
                <MsgType><![CDATA[%s]]></MsgType>
                <Content><![CDATA[%s]]></Content>
                </xml>'''

        resp = make_response(reply % (ToUserName, FromUserName, str(int(time.time())),MsgType, Content))

        resp.content_type = 'application/xml'

        return resp

    if(MsgType == 'image'):

        print(Msg.ToUserName, Msg.FromUserName, Msg.MsgType, Msg.CreateTime, Msg.MsgId)

        PicUrl = Msg.PicUrl
        MediaId = Msg.MediaId

        print(Msg.PicUrl,Msg.MediaId)

        reply = '''<xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%s</CreateTime>
                <MsgType><![CDATA[%s]]></MsgType>
                <Image>
                    <MediaId><![CDATA[%s]]></MediaId>
                </Image>
                </xml>'''

        resp = make_response(reply % (ToUserName, FromUserName, str(int(time.time())), MsgType, MediaId))

        resp.content_type = 'application/xml'

        return resp

    return 'success'

def addTail(s, status):
    if status == 0:
        s += '\n\n/**已经进入【睡眠模式】，发送0唤醒**/'
    elif status == 1:
        s += '\n\n/**您现在是【点菜模式】，发送【 #(id,id, ...) 】点菜，发送‘0’获取菜单，发送‘#’退出，不知道干啥可以【发送‘？’发现新世界】，发送‘h’查看历史订单，发送其他任意内容可以和我聊天哦~~**/'
    elif status == 2:
        s += '\n\n/**您还有未确认的订单，请确认**/'

    return s

def ReplyEventMsg(Msg):

    ToUserName = Msg.ToUserName
    FromUserName = Msg.FromUserName
    MsgType = Msg.MsgType
    CreateTime = Msg.CreateTime

    if MsgType != 'event':
        
        return DefaultReply(FromUserName, ToUserName)

    Event = Msg.Event

    if Event == 'subscribe':

        u = User.query.filter_by(wxid=FromUserName).first()

        if u is None:
            u = User(wxid=FromUserName, status = 0, role = 0, lastorder = 0)
            db.session.add(u)
            db.session.commit()

            return TextMsg(None,FromUserName, ToUserName, '/**【新客人，欢迎您】小e正在睡觉中，发送‘0’唤醒。。。**/')
            
        else:

            status = u.status
            if status == 0:
                return TextMsg(None,FromUserName, ToUserName, '/**【欢迎回来】，正在睡觉中，发送‘0’唤醒。。。**/')

            elif status == 1:
                return TextMsg(None,FromUserName, ToUserName, '/**【欢迎回来】，**/\n\n/**您上一次离开处于【点菜模式】，发送【#(id,id, ...)】点菜，发送‘0’获取菜单，发送‘h’查看历史订单，不知道干啥可以【发送‘？’发现新世界】，发送‘#’退出，发送其他任意内容可以和我聊天哦~~**/')

            elif status == 2:
                lo = Order.query.filter_by(id = u.lastorder).first()

                if lo is not None:

                    db.session.delete(lo)
                    db.session.commit()

                    reply = '/**【欢迎回来】，您在上一次离开之前有订单未确认，已自动为您撤销**/'
                    
                    u.status = 0
                    u.lastorder = 0
                    db.session.add(u)
                    db.session.commit()

                    reply = addTail(reply, u.status)
                    return TextMsg(None,FromUserName, ToUserName, reply)

                reply = '/**【欢迎回来】,您在上一次离开时状态异常，已自动为您回复初始状态**/'

                u.status = 0
                u.lastorder = 0
                db.session.add(u)
                db.session.commit()
                reply = addTail(reply, u.status)
                return TextMsg(None,FromUserName, ToUserName, reply)

    else:

        return DefaultReply(FromUserName, ToUserName)

def ReplyTextMsg(Msg):

    ToUserName = Msg.ToUserName
    FromUserName = Msg.FromUserName
    MsgType = Msg.MsgType
    CreateTime = Msg.CreateTime
    MsgId = Msg.MsgId

    if MsgType != 'text':
        
        return DefaultReply(FromUserName, ToUserName)

    u = User.query.filter_by(wxid=FromUserName).first()

    if u is None:
        u = User(wxid=FromUserName,status = 0, role = 0, lastorder = 0)
        db.session.add(u)
        db.session.commit()

    status = u.status
    role = u.role

    Content = Msg.Content

    if role == 1:

        if Content == '&':
            u.status = 3
            db.session.add(u)
            db.session.commit()

            return TextMsg(None,FromUserName, ToUserName, '/**已经进入【工作模式】，发送‘#’退出，发送‘0’查看当前订单**/')

    if status == 0:
    
        reply = '编号  名字  价格\n'

        if Content == '0':

            foods = Food.query.all()

            for food in foods:
                reply += '%d  %s   %.1f\n' % (food.id, food.name, food.price)


            reply += '\n\n'
            reply += '遵循召唤而来，为您奉上菜谱？\n\n'
            reply += '操作说明——例子：发送【 #(1，2，3) 】分别点编号为1，2，3的菜,不区分中英文括号和逗号\n\n'
            reply += '/**您已进入【点菜模式】，发送‘0’再次获取菜单，发送‘h’查看历史订单，不知道干啥可以【发送‘？’发现新世界】，发送‘#’退出**/\n\n'
            reply += '/**您有什么想说的可以和我说说哦，我可是能陪您聊聊天的~~*/'

            u.status = 1
            db.session.add(u)
            db.session.commit()

            return TextMsg(None,FromUserName, ToUserName, reply)

        else:

            return TextMsg(None,FromUserName, ToUserName, 'zzz...')

    elif status == 1:
        
        reply = ''
        con = ''

        for c in Content:
            if c == '（':
                c = '('

            if c == '）':
                c = ')'

            if c == '，':
                c = ','

            if c == '？':
                c = '?'

            con += c
 
        if Content == '0':
            reply = '编号  名字  价格\n'

            foods = Food.query.all()

            for food in foods:
                reply += '%d  %s   %.1f\n' % (food.id, food.name, food.price)

            return TextMsg(None,FromUserName, ToUserName, reply) 

        if Content == 'h' or Content == 'H':

            reply = ''
            count = 0

            orders = Order.query.order_by(Order.id.desc()).limit(5).all()
            
            reply += '/**您的历史订单情况如下：\n'

            for order in orders:

                if order.user_id == u.id:

                    count += 1
                    reply += '\n订单编号：'
                    reply += str(order.id)
                    reply += '\n'

                    reply += '订单内容：【'

                    details = OrderDetail.query.filter_by(order_id = order.id).all()

                    for detail in details:
                        food = Food.query.filter_by(id = detail.food_id).first()
                        reply += food.name
                        reply += ' '
                    reply += '】\n'


                    if order.confirmed == 2:
                        reply += '状态：排队完成'
                    elif order.confirmed == 1:
                        reply += '状态：已确认，正在排队'
                    else:
                        reply += '状态：异常'
                    reply += '\n'

                    reply += '**/'

                    reply += '\n/****/\n\n'

            if count != 0:
                reply += '/**以上是您的历史5个订单~~**/'
            else:
                reply += '/**找不到您之前的订单哦~~**/'

            reply = addTail(reply, u.status)
            return TextMsg(None,FromUserName, ToUserName, reply)

        if con == '?':

            re = ''

            re += '天气：例——发送：福州天气\n'
            re += '水果价格：例——发送：福州香蕉价格\n'
            re += '公交路线：例——发送：福州大学到上街镇公交路线\n'
            re += '电影：例——发送：电影推荐\n'
            re += '计算：例——发送：sin 2.4 * log 2 3 减 二的三次方\n'
            re += '图片：例——发送：表情包图片\n'
            re += '笑话：例——发送：笑话'

            return TextMsg(None,FromUserName, ToUserName, re)
        
        if con[0] == '#':

            if len(con) == 1:

                u.status=0
                db.session.add(u)
                db.session.commit()

                return TextMsg(None,FromUserName, ToUserName, '*******点菜结束,进入睡眠模式*******')

            else:
                li = getFoodNumList(con)

                if li is not None:
                    foodNameList = []

                    price = 0

                    ord = Order(user_id = u.id)
                    ord.confirmed = 0
                    db.session.add(ord)

                    for food_id in li:
                        fo = Food.query.filter_by(id=food_id).first()
                        if fo is not None:
                            price += fo.price
                            foodNameList.append(fo.name)
                            ordDetail = OrderDetail.from_json({'food_id':food_id, 'order_id':ord})
                            db.session.add(ordDetail)

                        else:
                            return TextMsg(None,FromUserName, ToUserName, '/**您点的菜中有不存在的哦，请不要瞎点~~**/')              

                    db.session.commit()

                    u.status = 2
                    u.lastorder = ord.id
                    db.session.add(u)
                    db.session.commit()

                    
                    reply = ''

                    reply += '/**您的订单：【 '

                    for name in foodNameList:
                        reply += name
                        reply += ' '

                    reply += '】 总价格: '
                    reply += str(price)

                    reply += '  确认中。。。\n\n回复y确认，回复n撤销**/'

                    return TextMsg(None,FromUserName, ToUserName, reply)

                else:
                    return TextMsg(None,FromUserName, ToUserName, '/**点菜格式出错啦，正确格式为:\n#(id,id, ...)，不然我不能识别啊**/')

        else:
            
            return TextMsg(None,FromUserName, ToUserName, talktoe.talk(Content, u.id))

    elif status == 2:
        lo = Order.query.filter_by(id = u.lastorder).first()

        if lo is None:

            u.status=0
            db.session.add(u)
            db.session.commit()

            reply = ''
            reply += '/**系统出现错误，已为您恢复初始状态，发送0开始点菜**/'

            return TextMsg(None,FromUserName, ToUserName, reply)

        foodNameList = []

        details = OrderDetail.query.filter_by(order_id = lo.id).all()

        for detail in details:
            food = Food.query.filter_by(id = detail.food_id).first()

            foodNameList.append(food.name)

        if Content == 'y' or Content == 'Y':
            lo.confirmed = 1

            db.session.add(lo)
            db.session.commit()

            reply = ''

            reply += '/**您的订单：【 '

            for name in foodNameList:
                reply += name
                reply += ' '

            reply += '】 已确认，后台苦力正在帮您排队~~**/'

            u.status = 1
            u.lastorder = 0
            db.session.add(u)
            db.session.commit()

            reply = addTail(reply, u.status)
            return TextMsg(None,FromUserName, ToUserName, reply)

        elif Content == 'n' or Content == 'N':

            db.session.delete(lo)
            db.session.commit()

            reply = ''

            reply += '您的订单：【 '

            for name in foodNameList:
                reply += name
                reply += ' '

            reply += '】 已撤销'
            

            u.status = 1
            u.lastorder = 0
            db.session.add(u)
            db.session.commit()

            reply = addTail(reply, u.status)
            return TextMsg(None,FromUserName, ToUserName, reply)

        else:
            reply = '您还不能做别的事哦，因为'

            reply += '您的订单：【 '

            for name in foodNameList:
                reply += name
                reply += ' '

            reply += '】 确认中。。。\n\n回复y确认，回复n撤销'

            return TextMsg(None,FromUserName, ToUserName, reply)

    elif status == 3:
        
        reply = ''
        count = 1

        if Content == '#':
            u.status = 0
            u.lastorder = 0
            db.session.add(u)
            db.session.commit()

            return TextMsg(None,FromUserName, ToUserName, '/**退出【工作模式】，进入【睡眠模式】。。。发送‘0’唤醒**/')

        if Content == '0':

            orders = Order.query.all()
            flag = False

            for order in orders:

                if order.confirmed == 1:
                    flag = True
                    reply += '订单编号：'
                    reply += str(order.id)
                    reply += '\n'

                    foodNameList = []

                    details = OrderDetail.query.filter_by(order_id = order.id).all()

                    for detail in details:
                        food = Food.query.filter_by(id = detail.food_id).first()

                        foodNameList.append(food.name)
                        reply += food.name
                        reply += ' '

                    reply += '\n/*****/\n\n'
            if flag:

                reply += '发送对应订单编号确认排队完成\n'
                reply += '/*****/'

            else:
                reply += '/**目前没有订单**/'

            return TextMsg(None,FromUserName, ToUserName, reply)

        if re.match('^[0-9]+$', Content):

            o = Order.query.filter_by(id = int(Content)).first()

            if o is None:
                return TextMsg(None,FromUserName, ToUserName, '/**没有该订单**/')

            if o.confirmed == 0:
                return TextMsg(None,FromUserName, ToUserName, '/**该订单未确认**/')

            o.confirmed = 2
            db.session.add(o)
            db.session.commit()

            orders = Order.query.all()
            flag = False

            for order in orders:

                if order.confirmed == 1:
                    flag = True
                    reply += '订单编号：'
                    reply += str(order.id)
                    reply += '\n'

                    foodNameList = []

                    details = OrderDetail.query.filter_by(order_id = order.id).all()

                    for detail in details:
                        food = Food.query.filter_by(id = detail.food_id).first()

                        foodNameList.append(food.name)
                        reply += food.name
                        reply += ' '

                    reply += '\n/*****/\n\n'
            if flag:

                reply += '发送对应订单编号确认排队完成\n'
                reply += '/*****/\n\n'

            else:
                reply += '/**目前没有订单**/\n\n'

            reply += '/**订单'
            reply += str(o.id)
            reply += '确认排队完成**/'

            return TextMsg(None,FromUserName, ToUserName, reply)
        
        return TextMsg(None,FromUserName, ToUserName, '工作中，请认真工作')


    return DefaultReply(FromUserName, ToUserName)