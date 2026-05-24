import sys
import os
import logging
import asyncio
logging.getLogger(__name__)#同步主文件的日志格式

#仅允许main.py调用
from elaina.plugin.user_ai_msgreply import auto_reply_message as _user_ai
from elaina.plugin.tools_use import send_msg,User,get_formatted_time

async def ai_auto_reply_message(data:dict):
    return await _user_ai(data)
