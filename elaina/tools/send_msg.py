import httpx
import logging
import os
import sys

from elaina.common.setting import *

logging.getLogger(__name__)#同步主文件的日志格式

async def send_msg(msg,uid : int,gid : int,mid = None) -> None:
    """发送信息"""
    url = server_address
    data = {}
    if gid is not None:#优先判断群聊
        url+='/send_group_msg'
        data.update({'group_id':gid})
    else:
        url+='/send_private_msg'
        data.update({'user_id':uid})
    
    if mid is not None:#若引用不为None，则引用该信息
        data.update({'message':f'[CQ:reply,id={mid}]{msg}'})
    else:
        data.update({'message':f'{msg}'})
    
    try:
        async with httpx.AsyncClient() as client:#使用异步调用post
            await client.post(url,json=data,timeout=5)
        logging.debug('已发送消息')
        #但愿以后我用不到这行requests
        #requests.post(url,json=data,timeout=5)
    except:
        logging.exception('send_msg出现错误,呃,我也不知道是啥')