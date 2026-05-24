import sys
import os
import logging
logging.getLogger(__name__)#同步主文件的日志格式

#工具函数    仅允许plugin和main.py使用
from elaina.tools.send_msg import send_msg as _send_message
from elaina.tools.user_json import User as _Users
from elaina.tools.time_get import get_formatted_time as _get_time

#对外提供接口
async def send_msg(msg,uid : int,gid : int,mid = None):
    """发送信息  
    没啥需要特别注意的,照着填就行
    """
    return await _send_message(msg,uid,gid,mid)

def User(uid,path):
    """创建用户对象"""
    return _Users(uid,path)

def get_formatted_time():
    """返回当前时间，格式为 '年份-月份-日期-小时:分钟:秒'"""
    return _get_time()
