#include "DjjMsgQue.h"

#define WEB_SERVER_KEY  1111
#define IO_BOX_KEY		2222
#define MSGSIZE 1024


static int Web2IO_id = -1;
static int Io2Web_id = -1;

static int g_character = -1;

typedef struct msg_st
{
	long int msg_type;
	char content[MSGSIZE];
}TDjjMsg;


//创建两个队列用于两个进程之间的互相通信
int MsgQueInit()
{
	Web2IO_id = msgget((key_t)WEB_SERVER_KEY, 0666 | IPC_CREAT);
	Io2Web_id = msgget((key_t)IO_BOX_KEY, 0666 | IPC_CREAT);

	if (Web2IO_id == -1 || Io2Web_id == -1)
	{
		return DJJ_FAILURE;
	}

	return DJJ_SUCCESS;
}

int SetCharacter(int character)
{
	//1表示web, 2表示IO_box;
	g_character = character;
}

int MsgQueSend(long msg_type, void* buf, size_t bufSize)
{
	TDjjMsg msg;
	memset(&msg, 0, sizeof(TDjjMsg));
	msg.msg_type = msg_type;
	memcpy(msg.content, buf, (bufSize>1024?1024:bufSize));
	if (g_character == 1)
	{
		if (msgsnd(Web2IO_id, (void*)&msg, MSGSIZE, 0) == -1)
			return DJJ_FAILURE;		
	}
	if (g_character == 2)
	{
		if (msgsnd(Io2Web_id, (void*)&msg, MSGSIZE, 0) == -1)
			return DJJ_FAILURE;
	}

	return DJJ_SUCCESS;
}

int MsgQueRcv(long* msg_type, void* dst)
{
	TDjjMsg msg;
	memset(&msg, 0, sizeof(TDjjMsg));
	if (g_character == 1)
	{	
		if (msgrcv(Io2Web_id, (void*)&msg, MSGSIZE, 0, IPC_NOWAIT) == -1)
			return DJJ_FAILURE;
	}
	if (g_character == 2)
	{
		if (msgrcv(Web2IO_id, (void*)&msg, MSGSIZE, 0, IPC_NOWAIT) == -1)
			return DJJ_FAILURE;
	}

	*msg_type = msg.msg_type;
	memcpy(dst, msg.content, MSGSIZE);
	return DJJ_SUCCESS;
}

int MsgQueDel()
{
	int ret1, ret2;
	ret1 = msgctl(Web2IO_id, IPC_RMID, 0);
	ret2 = msgctl(Io2Web_id, IPC_RMID, 0);
	
	if (ret1 == -1 || ret2 == -1)
	{
		return DJJ_FAILURE;
	}
	return DJJ_SUCCESS;
}