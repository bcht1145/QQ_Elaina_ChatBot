from config import *
from fastapi import *
from datetime import datetime
from fastapi.responses import *
import os
import json
import requests
import ast
import logging
import config
import importlib
import ota
import uvicorn
import httpx
import asyncio
import aiofiles

from elaina.common.plugin import ai_auto_reply_message,send_msg

#首先，去他丫的LOGO
#我肯定是不会写LOGO，占地

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
    )
#在没有错误日志的情况下诊断任何问题无异于闭眼开车——Apache官方文档
logging.getLogger(__name__)

path =  os.path.dirname(__file__) #文件路径
logging.debug(f'路径:{path}')
if not os.path.exists(os.path.join(path,'user_json')):#初始化ing
    logging.warning('用户数据库不存在，创建')
    os.makedirs(os.path.join(path,'user_json'))
if not os.path.exists(os.path.join(path,'group_json')):
    logging.warning('群聊数据库不存在，创建')
    os.makedirs(os.path.join(path,'group_json'))

server = FastAPI(title='Elaina')
client_version = 'v2.0.0'# 机器人版本，用于OTA，不要修改
file_lock = asyncio.Lock() #谁持锁，这文件就是谁的天下。函数啊，大文件…就给你了…(趋势)(大清就交给你了)
user_locks = {}  # 存储每个用户的锁
keep_file = ['config.py','user_json','group_json']

def get_formatted_time():
    """返回当前时间，格式为 '年份-月份-日期-小时:分钟:秒'"""
    return datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

# def hot_reload_config():
#     """用于热重载配置文件"""
#     logging.info('正在热重载配置文件')
#     importlib.reload(config)
#     globals().update({k: v for k, v in vars(config).items() if not k.startswith("_")})
#     """
#     我承认这一大堆我也看不懂
#     反正就是把那一大堆变量读进来,赋值给全局变量
#     并且忽视私有变量(下划线开头)
#     """
"""
因为主要的功能被移到后端了,因此热加载不能用了QAQ
"""

async def get_user_lock(uid: int):
    """获取用户专属的异步锁"""
    async with file_lock:
        if uid not in user_locks:
            user_locks[uid] = asyncio.Lock()
        return user_locks[uid]

@server.post('/')
async def auto_reply_message(data: dict):
    uid = data.get("user_id")#目标qq
    gid = data.get("group_id")#群聊qq
    mid = data.get("message_id")#消息编号
    msg = data.get("raw_message")#消息

    if msg is not None and (msg[0]=='/' or msg.startswith(f'[CQ:at,qq={bot_qq}]')):#若消息不为空，且开头为斜杠或at的情况下受理
        msg = msg.replace("&#91;", "[").replace("&#93;", "]").replace("&amp;", "&").replace("&#44;", ",")#转码
        data['msg'] = msg
        if uid==2854196310:#这里是防Q群管家
            logging.debug('Q群管家at你了')
            return {}
        await ai_auto_reply_message(data)

        if msg == '/help':#用于获取帮助
            try:
                with open('help.txt','r',encoding='utf-8') as f:#防手欠x2
                    await send_msg(f'{f.read()}',uid,gid)
            except FileNotFoundError:
                await send_msg('未找到帮助文档文件',uid,gid)
                logging.exception('未找到帮助文档文件，请确认help.txt是否存在且未重命名')
                return {}
            return {}
        
    return {}

if __name__ == '__main__':#但愿没人闲的没事把这玩意当模块跑
    logging.info(f'当前版本:{client_version}')
    if OTA_allow:
        logging.info('正在检查更新...')
        success, msg = ota.ota_update(client_version, github_repo, auto_restart=True)
        logging.info(msg)
        
    uvicorn.run(server,host=client_address,port=client_port)#每日禁用debug(1/1)
