#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify, send_from_directory, make_response
import json
# import SocketServer
from ctypes import *
import types
from threading import Lock
from eventlet.green import threading
import time
from flask_socketio import SocketIO, emit
from werkzeug import secure_filename
from functools import wraps
import re

"""
app = Flask(__name__)
recvMsg = 1
sendMsg = 1
queInit = 1
setCharacter = 1


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


@app.route('/', methods=['POST', 'GET'])
def index():
	if request.method == 'GET':
		print("receive GET Request")
		return render_template('index.html')
	if request.method == 'POST':
		print("receive POST Request")
		# data = json.dumps(request.get_json())
        # msgTranslate(json.loads(data))
		msgTranslate(json.dumps(request.get_json()))
	return jsonify({'OK': True}), 200


@app.route('/answer', methods=['POST', 'GET'])
def answer():
	if request.method == 'GET':
		print("receive ask GET request")
	if request.method == 'POST':
		print("receive ask POST request")
		data = json.dumps(request.get_json())
		print(data)
		l = ['name','djj']
		return jsonify(l)
	
	
def msgTranslate(msg):
	print(type(msg))
	print(msg)
	bData = bytes(str(msg))
	sendMsg(100, bData, 1024)

	

def recvThread():
	while True:
		print("recvThread start---")
		msgNum = c_long(0)
		content = create_string_buffer(1024)
		if recvMsg(byref(msgNum), content) == 0:
			print(content)
			print("the content number is %d, the content is:%s" % (msgNum.value, content.value))
		else:
			time.sleep(1)
			print("sleep 1s")
	
	
if __name__ == '__main__':
	loadDjjque()
	isInit = queInit()
	setCharacter(1)
	if isInit == 0:
		print("--queInit success--")
	t = threading.Thread(target=recvThread, name='recvThread')
	t.setDaemon(True)
	t.start()
	app.run(host='0.0.0.0', port=5555)
"""

async_mode = "threading"
app = Flask(__name__)
# flask的配置项,项目较小直接写在脚本中
app.config.update(
    SECRET_KEY = 'secret',
    UPLOAD_FOLDER = '/home/samba/web_server/uploads',
    ALLOWED_EXTENSIONS = set('txt pdf png jpg jpeg pkg'.split()),
    MAX_CONTENT_LENGTH = 50*1024*1024,
)
socketio = SocketIO(app, async_mode=None)
thread = None
recvMsg = None
sendMsg = None
queInit = None
setCharacter = None
thread_lock = Lock()

#消息定义
MSG_CHANGE_IP   = 100
MSG_REBOOT      = 101
MSG_REBOOT_ACK  = 102

MSG_PROOF_TIME  = 103
MSG_PROOF_ACK   = 104

MSG_SIGNAL_CONTROL_SET=105
MSG_SIGNAL_CONTROL_SET_ACK = 106

MSG_SIGNAL_CONFIG_QUERY = 107
MSG_SIGNAL_CONIFG_QUERY_ACK = 108

MSG_REAL_TIME_RECORD = 109

CONTROL_SIGNAL_FILE = "/home/work/IOBOX/contrCfg"

#设置信号机配置
@socketio.on('signal_control')
def signal_control(request):
    print('SERVER_from_web: signal control:'+ request)
    msgTranslate(MSG_SIGNAL_CONTROL_SET, request)


# changeIP
@socketio.on('change_ip')
def handle_request(request):
    print('SERVER_from_web: Change IPConfig:' + request)
    msgTranslate(MSG_CHANGE_IP ,request)

# MSG_REBOOT_ACK
@socketio.on('reboot_ack')
def reboot_ack():
    print('SERVER_from_web: Reboot ack')
    msgTranslate(MSG_REBOOT_ACK, None);

#校时
@socketio.on('proof_time')
def proof_time(data):
    print('SERVER_from_web: proof_time:'+ data)
    msgTranslate(MSG_PROOF_TIME, data)

# 在web-socket连接的时候开启新线程
@socketio.on('connect')
def connect():
	print('SERVER: one websocket connect')
	d = get_net_address()
	if(d != None):
		print("SERVER_to_web: show netinfo:" + str(d))
		socketio.emit("showIP", json.dumps(d))
	config = get_signal_control_config()
	if(config != None):
		print("SERVER_to_web: show signal_config:" + config)
		socketio.emit('signal_config', config)

#接收到升级包之后升级
@socketio.on('update')
def update():
    print('SERVER_from_web: receive a pkg file, now update!')
    pass


#断开socket链接
@socketio.on('disconnect')
def disconnect():
    print('SERVER: one websocket disconnect')


#跨域装饰器
def allow_cross_domain(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        rst.headers['Access-Control-Allow-Origin'] = '*'
        rst.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
        allow_headers = "Referer,Accept,Origin,User-Agent"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        return rst
    return wrapper_fun


# 路由绑定 '/'
@app.route('/', methods=['POST', 'GET'])
@allow_cross_domain
def index():
	if request.method == 'GET':
		print("receive GET Request")
		return render_template('index.html')
	if request.method == 'POST':
		print("receive POST Request")
		print(request.get_json())
	return jsonify({'OK': True}), 200


# 加载消息队列的库
def loadDjjque():
    rt = CDLL('./libMsgQue_sdk.so')
    global queInit
    queInit = rt.MsgQueInit
    queInit.argtypes = None
    queInit.resType = c_int

    global recvMsg
    recvMsg = rt.MsgQueRcv
    recvMsg.argtypes = (POINTER(c_long), c_char_p)
    recvMsg.resType = c_int

    global sendMsg
    sendMsg = rt.MsgQueSend
    sendMsg.argtypes = (c_long, c_char_p, c_size_t)
    sendMsg.resType = c_int

    global setCharacter
    setCharacter = rt.SetCharacter
    setCharacter.argtypes = (c_int,)
    setCharacter.restype = c_int


# 转发消息给IO盒子
def msgTranslate(msgNum, msgContent):
    if msgContent is None:
        bData = bytes('', encoding='utf-8')
    else:
        bData = bytes(msgContent, encoding="utf-8")
    print("SERVER_to_IO: msgNum:%s ,msgContent:%s"% (msgNum, bData))
    sendMsg(msgNum, bData, 1024)

#修改ip,重启
def need_Reboot(newIP):
	with app.app_context():
		socketio.emit("need_Reboot", newIP)

#时间校验ack
def proof_time_ack(data):
    with app.app_context():
        socketio.emit("proof_time_ack", data)

#信号机控制ack
def signal_control_set_ack(data):
    with app.app_context():
        socketio.emit("signal_control_set_ack", data)

#实时过车消息：消息内容为下,在这里解析好发送给前段
"""
 Uint8 msgBuf[32] = {0};

    msgBuf[0] = 0xfe;
    msgBuf[1] = 0xfe;
    if(0 == coilState)
    {
        /*离开*/
        msgBuf[2] = 0x00 + landID%0x17;
    }
    else
    {
        /*进入*/
        msgBuf[2] = 0x80 + landID%0x17;
    }
    msgBuf[3] = 0x55;

"""
def real_time_record(data):
    with app.app_context():
        #解析bytes类型的data,第三位为过车车道及过车的信息
        #大于128表示有过车信息
        d = {}
        if(data[2] >= 128):
            d["roadId"] = int(data[2]-128)+1
            d["enable"] = 1
        else:
            d["roadId"] = int(data[2])+1
            d["enable"] = 0
        print(json.dumps(d))
        socketio.emit("real_time_record", json.dumps(d))

#根据函数名调用对应的函数, 类似于C的 switch: case;
def msgType_to_functions(msgType, arg):
	swicther = {
        MSG_REBOOT: "need_Reboot",
        MSG_PROOF_ACK: "proof_time_ack",
        MSG_SIGNAL_CONTROL_SET_ACK: "signal_control_set_ack",
        MSG_REAL_TIME_RECORD: "real_time_record",
	}
	func = globals().get(swicther.get(msgType))
	return func(arg)


# 处理IO盒子发来的消息的线程
def recvThread():
	msgNum = c_long(0)
	content = create_string_buffer(1024)
	print('thread starting')
	while True:
		if recvMsg(byref(msgNum), content) == 0:
			print("SERVER_from_IO : the content type is %s, the content number is %d, the content is:%s" % (type(content.value), msgNum.value, content.value))
			if(msgNum.value == MSG_REAL_TIME_RECORD):
				#create_string_buffer的value属性是将它当成一个\0结尾的字符串获取值，raw属性是当成字节流
				msgType_to_functions(msgNum.value, content.raw)
			else:
				msgType_to_functions(msgNum.value, str(content.value, encoding='utf-8'))
		else:
			# 必须要用socketio.sleep()才能正确的释放锁,让消息继续循环下去
			socketio.sleep(1)


# 返回允许上传的文件名
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# 这个函数其实是用来下载文件的，这里是用来作为url_for的第一个参数来获取上传文件的url
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    print(send_from_directory(app.config['UPLOAD_FOLDER'],filename))
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

#上传文件路由
@app.route('/up', methods=['POST', 'GET'])
def upload_file():
	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # url_for 获取重定向之后的url地址,即 uploaded_file函数 指向的url，这里为:/uploads/filename
			file_url = url_for('uploaded_file', filename=filename)
	return jsonify({'OK': True}), 200


# 查询IP,Mask,Gateway
def get_net_address():
	d = {}
	try:
		with open('/etc/network/interfaces', 'r') as f:
			lines = f.readlines()
			for l in lines:
				if "address" in l:
					d['IO_address'] = l.split(' ')[1].replace('\n','')
				if "netmask" in l:
					d['IO_mask'] = l.split(' ')[1].replace('\n','')
				if "gateway" in l:
					d['IO_gateway'] = l.split(' ')[1].replace('\n','')
		return d
	except IOError:
		print("SERVER: open /etc/network/interfaces failed")
		return None


# 查询信号机配置文件
def get_signal_control_config():
	try:
		with open(CONTROL_SIGNAL_FILE) as f:
			return f.read()
	except IOError:
		print("SERVER: open control signal config file failed")
		return None


if __name__ == '__main__':
    loadDjjque()
    isInit = queInit()
    setCharacter(1)
    if isInit == 0:
        print("SERVER: --MsgQue init success--")
    with thread_lock:
        if thread is None:
            socketio.start_background_task(target=recvThread)
    socketio.run(app, host='0.0.0.0', port=5555)








