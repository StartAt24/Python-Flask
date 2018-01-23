#include "DjjMsgQue.h"
#include <unistd.h>
#include "rapidjson/document.h"
#include "rapidjson/prettywriter.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"
#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h> 
using namespace rapidjson;

int main()
{
	//system("sudo python3.4 /home/samba/DJJ/python_server/install_sourcefile/checkModule.py");
	//system("sudo python3.4 /home/samba/web_server/server.py &");
	//等待web启动完成.
	sleep(2);
	if (MsgQueInit() == -1)
	{
		printf("Init failed \n"); 
		return -1;
	}

	printf("Init success \n");
	SetCharacter(2);
	

	long msg_type;
	char dst[1024] = { 0 };
	
	while(true)
	{
		printf("now while \n");
		if (MsgQueRcv(&msg_type, dst) == 0)
		{
			/*
			Document document;
			document.Parse<0>(dst);

			//打印值
			Value& node1 = document["ip"];
			printf("ip is %s\n", node1.GetString());

			Value& node2 = document["cover"];
			printf("cover is %s\n", node2.GetString());

			Value& node3 = document["gate"];
			printf("gate is %s \n",node3.GetString());

			KOSA_NetIf netif;
			memset(netif.devname, 0, 7);
			memset(netif.ethaddr, 0, 6);
			netif.dhcp = 0;
			netif.ipaddr = htonl(inet_addr(node1.GetString()));
			netif.netmask = htonl(inet_addr(node2.GetString()));
			netif.gateway = htonl(inet_addr(node3.GetString()));
			printf("ipaddr:%ul, netmask:%ul, gateway:%ul\n", netif.ipaddr, netif.netmask, netif.gateway);
			KOSA_setIPaddr(&netif);
			*/
			
			//解析发来的json数据
			Document document;
			document.Parse<0>(dst);
			
			printf("first line\n");
			//发送一条消息给web表示，设置ip成功
			Value& node1 = document["ip"];
			printf("ip is %s\n", node1.GetString());

			Value& node2 = document["cover"];
			printf("cover is %s\n", node2.GetString());

			Value& node3 = document["gate"];
			printf("gate is %s \n",node3.GetString());
			
			
			//组成json数据转发回去
			Document doc;
			doc.SetObject();
			//获取分配器
			Document::AllocatorType &allocator = doc.GetAllocator();
			//给doc对象赋值
			const char name[] = "daijunjie";
			doc.AddMember("name", name, allocator);
			//添加数组型数据
			Value array1(kArrayType);
			/*
			for (int i=0;i<3;i++)
			{
				Value int_object(kObjectType);
				int_object.SetInt(i);
				array1.PushBack(int_object, allocator);
			}
			doc.AddMember("number", array1, allocator);
			*/
			
			//将doc对象的值写入字符串
			StringBuffer buffer;
			Writer<StringBuffer> writer(buffer);
			doc.Accept(writer);
			
			char buf[1024] = {0};			
			int count = 1;
			memcpy(buf, buffer.GetString(), buffer.GetSize());
			
			printf("IO: buffer is:%s ,size is %d\n", buf, buffer.GetSize());			
			
			while(count>0)
			{
				if (MsgQueSend(111, buf, 1024) == -1)
				{
					printf("MsgQueSend failed\n");
				}
				printf("MsgQueSend success\n");		
				sleep(7);
				count--;
			}
			MsgQueDel();
			break;
		}
		else
		{
			sleep(1);
			printf("Sleep 1 sec\n");
		}
	}

	return 1;
}
