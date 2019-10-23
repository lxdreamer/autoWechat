from flask import Flask
from flask import request
import hashlib
import requests
import base64
import os,string,glob
import json
import time
import random
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlencode


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/wx', methods=["GET","POST"])
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
            return reply_text(fromUser, toUser, replyTX(content))
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

def replyTX(msg):
    myMsgTencent = MsgTencent()
    params = {
        'app_id': myMsgTencent.getAppId(),
        'session': '10000',
        'question': msg.encode('utf8'),
        'time_stamp': myMsgTencent.get_time_stamp(),
        'nonce_str': myMsgTencent.get_random_str()
	}
    params['sign'] = myMsgTencent.gen_dict_md5(params,myMsgTencent.getAppKey())
    url = 'https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat'

    paramsJson = urlencode(params)
    print(paramsJson)
    r = requests.post(url, headers={"Content-Type" : "application/x-www-form-urlencoded"},data= paramsJson).json()
    print(r)
    return r['data']['answer']


class MsgTencent(object):
    def __init__(self,App_id=None,App_key=None):
        if not App_id: AppID = '2123068912'
        if not App_key: AppKey = '0xZZis1wBdL0zKqy'
        self.app_id= AppID 
        self.app_key= AppKey
    def getAppId(self):
        return self.app_id;
    def getAppKey(self):
        return self.app_key;

    def get_random_str(self):
        #随机生成16位字符串
        rule = string.ascii_lowercase + string.digits
        str = random.sample(rule, 16)
        return "".join(str)
    
    def get_time_stamp(self):
        return str(int(time.time()))
		
    def gen_dict_md5(self,req_dict,app_key):
        if not isinstance(req_dict,dict) :return None 
        if not isinstance(app_key,str) or not app_key:return None 
        print(req_dict)
        try:            
            #方法，先对字典排序，排序之后，写app_key，再urlencode
            sort_dict= sorted(req_dict.items(), key=lambda item:item[0], reverse = False)
            sort_dict.append(('app_key',app_key))
            print(sort_dict)
            sha = hashlib.md5()
            rawtext= urlencode(sort_dict).encode()
            sha.update(rawtext)
            md5text= sha.hexdigest().upper()
            #print(1)
            #字典可以在函数中改写
            if md5text: req_dict['sign']=md5text
            return md5text
        except Exception as e:
            print(e)
            return   None

    #生成字典
    def gen_req_dict(self, req_dict,app_id=None, app_key=None,time_stamp=None, nonce_str=None):
        """用MD5算法生成安全签名"""
        if not req_dict.get('app_id'): 
            if not app_id: app_id= self.app_id
            req_dict['app_id']= app_id
       
        #nonce_str 字典无值
        if not req_dict.get('time_stamp'): 
            if not time_stamp: time_stamp= self.get_time_stamp()
            req_dict['time_stamp']= time_stamp
        
        if not req_dict.get('nonce_str'): 
            if not nonce_str: nonce_str= self.get_random_str()
            req_dict['nonce_str']= nonce_str
        #app_key 取系统参数。
        if not app_key: app_key= self.app_key        
        md5key= self.gen_dict_md5(req_dict, app_key)
        return md5key

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=80)
