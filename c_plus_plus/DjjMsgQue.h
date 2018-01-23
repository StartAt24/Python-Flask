
#ifndef _DJJMSGQUE_H_
#define _DJJMSGQUE_H_
#ifdef __cplusplus
extern "C"{
#endif
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <sys/msg.h>

#define DJJ_SUCCESS 0
#define DJJ_FAILURE -1

	int MsgQueInit(); 
	int MsgQueSend(long msg_type, void* buf, size_t bufSize);
	int MsgQueRcv(long* msg_type, void* dst);
	int MsgQueDel();

	int SetCharacter(int character);
#ifdef __cplusplus
}
#endif
#endif
 
