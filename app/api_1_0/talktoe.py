import json
from urllib import request, parse


def talk(s, id):
    url='http://www.tuling123.com/openapi/api'

    data = parse.urlencode([('key','43e72030fa2a4c5588b6c970d1cfcb7d'),('userid', str(id)), ('info',s), ('loc', '福州市')])

    req = request.Request(url)  

    result = request.urlopen(req,data=data.encode('utf-8')).read()  

    result = json.loads(result.decode('utf-8'))

    if result.get('code') == 40004:
        return '小e今天累了，请使用基本功能吧，发送【#(id,id, ...)】点菜，发送‘0’获取菜单，发送‘h’查看历史订单，发送‘#’退出'
    elif result.get('code') < 40010:
        return '小e脑子发生短路，发生了某些错误。。。'
    elif result.get('code') == 200000:
        return result.get('text') +'-----'+ '\n<a href = \' ' + result.get('url') + ' \'>看这里</a>'
    else:
        return result.get('text')