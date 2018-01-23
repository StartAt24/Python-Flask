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
	
	if (MsgQueInit() == -1)
	{
		printf("Init failed \n"); 
		return -1;
	}

	printf("Init success \n");
	SetCharacter(2);

	char msg[32] = {0};
	
	int roadNum = 1;
	
	while(1)
	{
		sleep(1);				
		msg[0] = 0xfe;
		msg[1] = 0xfe;
		msg[2] = 0x80 + roadNum%0x17;
		msg[3] = 0x55;
		
		roadNum ++;
		
		if(MsgQueSend(109, msg, sizeof(msg)) == -1)
		{
			printf("MsgQueSend failed\n");
		}
		printf("MsgQueSend success\n");
	}
	
}