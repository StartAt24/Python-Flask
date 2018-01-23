# Python-Flask
一个简单的运行在linux上的webserver,通过websocket实现了与前端的双向通信.通过ipc的消息机制与同设备上的C\C++程序实现数据通信。

具体实现方法可以看博客:http://blog.csdn.net/fengchu3415/article/details/78921413

列表中的daemon脚本是一个守护进程，可以开机的时候启动下，这样不管是C++程序(脚本中的net2io) 还是web_server，在进程退出的时候都会进行重启。

关于C++部分的实现简单的附加了一个例子，中间涉及到了json解析的部分及数据发送回web的部分，可以参考下。


