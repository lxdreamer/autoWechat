from flask import Flask
from flask import request
import hashlib
import requests
import json
import time
import re
import xml.etree.ElementTree as ET


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/wx', methods=["GET", "POST"])
def weixin():
    if request.method == "GET":
        my_signature = request.args.get('signature')  # 获取携带的signature参数
        my_timestamp = request.args.get('timestamp')  # 获取携带的timestamp参数
        my_nonce = request.args.get('nonce')  # 获取携带的nonce参数
        my_echostr = request.args.get('echostr')  # 获取携带的echostr参数

        token = 'lixiang'
        list = [token, my_timestamp, my_nonce] 
        list.sort()

        sha1 = hashlib.sha1()   
        sha1.update(list[0].encode('utf-8'))
        sha1.update(list[1].encode('utf-8'))
        sha1.update(list[2].encode('utf-8'))
        mysignature = sha1.hexdigest()


        # 加密后的字符串可与signature对比，标识该请求来源于微信
        if my_signature == mysignature:
            return my_echostr
    else:
        # 解析xml
        xml = ET.fromstring(request.data)
        toUser = xml.find('ToUserName').text
        fromUser = xml.find('FromUserName').text
        msgType = xml.find("MsgType").text
        createTime = xml.find("CreateTime")
        # 判断类型并回复
        if msgType == "text":
            content = xml.find('Content').text
            return reply_text(fromUser, toUser, reply(fromUser, content))
        else:
            return reply_text(fromUser, toUser, "我只懂文字")

def reply_text(to_user, from_user, content):
    """
    以文本类型的方式回复请求
    """
    return """
    <xml>
        <ToUserName><![CDATA[{}]]></ToUserName>
        <FromUserName><![CDATA[{}]]></FromUserName>
        <CreateTime>{}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{}]]></Content>
    </xml>
    """.format(to_user, from_user, int(time.time() * 1000), content)

def reply(openid, msg):
    '''
    使用图灵机器人
    '''
    data = {
        "userInfo": {
            "apiKey": "5cc891bbc29c4f9a9fede8e9a0611110",
            "userId": openid
        },
        "perception": {
            "inputText": {
                "text": msg
            },
            "inputImage": {
                "url": "imageUrl"
            },
            "selfInfo": {
                "location": {
                    "city": "北京",
                    "province": "北京",
                    "street": "信息路"
                }
            }
        }
    }
    r = requests.post('http://openapi.tuling123.com/openapi/api/v2',json.dumps(data)).json()
    msg =  r['results'][0]['values']['text']
    return msg


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=80)
