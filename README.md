# Python-Flask
一个简单的运行在linux上的webserver,通过websocket实现了与前端的双向通信.通过ipc的消息机制与同设备上的C\C++程序实现数据通信。

具体实现方法可以看博客:http://blog.csdn.net/fengchu3415/article/details/78921413

列表中的daemon脚本是一个守护进程，可以开机的时候启动下，这样不管是C++程序(脚本中的net2io) 还是web_server，在进程退出的时候都会进行重启。

关于C++部分的实现简单的附加了一个例子(在c_plus_plus文件夹下)，中间涉及到了json解析的部分及数据发送回web的部分，可以参考下。
其中的DjjMsgQue.cpp和DjjMsgQue.h即消息队列的封装.
io.cpp和realTimeTest.cpp都是简单的解析及返回数据。
编译指令:g++ -o io io.cpp -I ./include -I . 

运行环境是python3.4，联网条件下可以直接 pip3 install flask及 flask-socketio, flask-uploads
生产环境下，可以再install_sourcefile目录下执行 sudo python3.4 checkModule.py,自动安装整个项目依赖的模块。一共是14个模块，如果安装之后运行不了，可能是有的模块没有安装好，可以再次执行下sudo python3.4 checkModule.py。成功的话会提示 have enough modules? True.

