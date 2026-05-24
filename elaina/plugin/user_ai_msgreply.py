from openai import AsyncOpenAI
import asyncio
import json
import ast
import logging
import aiofiles
import httpx
import sys
import os

from elaina.common.tools import User,send_msg,get_formatted_time
from elaina.common.setting import *
from elaina.common.path import ROOT_PATH as path

logging.getLogger(__name__)#同步主文件的日志格式

file_lock = asyncio.Lock() #谁持锁，这文件就是谁的天下。函数啊，大文件…就给你了…(趋势)(大清就交给你了)
user_locks = {}  # 存储每个用户的锁

async def get_user_lock(uid: int):
    """获取用户专属的异步锁"""
    async with file_lock:
        if uid not in user_locks:
            user_locks[uid] = asyncio.Lock()
        return user_locks[uid]

async def auto_reply_message(data:dict):
    uid = data.get("user_id")#目标qq
    gid = data.get("group_id")#群聊qq
    mid = data.get("message_id")#消息编号
    msg = data.get("raw_message")#消息

    user = User(uid,path)#建立用户对象方便操作

    if msg == '/删除聊天记录':
        logging.info(f'{uid}删除了除好感度之外的所有记录')
        #删除处好感度以外的所有数据
        await send_msg('聊天记录已清除，其余未变',uid,gid)
        user_info = await user.load()
        user_info['message'] = []
        await user.write(user_info)
        return {}

    if msg == '/重置聊天记录':
        logging.info(f'{uid}删除了所有记录')
        #全清了！！！
        await send_msg('记录已全部删除',uid,gid)
        await user.delete()
        return {}

    if msg.startswith('/撤回上一条'):
        logging.info(f'{uid}撤回了上一条')
        user_info = await user.load()
        if user_info['message'] != []:#删两遍，因为同时有机器人和用户的对话，删的是一回合
            s = user_info['message'].pop()#如果没毛病，那这里就是机器人的回复了(没想到吧我pop()有返回值)
            user_info['message'].pop()
            user_info['time'].pop()
            if user_info['favor'] < 100:#对于防掉好感度，我还真没好的法子，只能检测是不是满的了
                user_info['favor'] = user_info['favor'] - ast.literal_eval(s['content'])['favor']#减就相当于反向操作了
            await user.write(user_info)
            await send_msg('已撤回，好感度恢复',uid,gid)
        else:
            logging.info(f'{uid}但他似乎没聊过…')
            await send_msg('你似乎没的可撤回…',uid,gid)

    if  msg.startswith('/查看好感度'):
        logging.info(f'{uid}查看了好感度')
        user_info = await user.load()
        await send_msg(f'当前好感度：{user_info["favor"]}',uid,gid)

    if msg.startswith('/查看上一条'):
        logging.info(f'{uid}查看了上一条')
        user_info = await user.load()
        if user_info['message'] != []:
            await send_msg(f'你：{user_info["message"][-2]['content']}\n我：{ast.literal_eval(user_info["message"][-1]['content'])['message']}\n时间：{user_info['time'][-1]}',uid,gid)
        else:
            logging.info(f'{uid}但似乎没的可回顾…')
            await send_msg('你似乎没的可回顾…',uid,gid)


    if msg.startswith(f'[CQ:at,qq={bot_qq}]') or msg.startswith('/AI'):#判断是否是AI聊天
        logging.info(f'{uid}触发了AI聊天')
        if msg.startswith(f'[CQ:at,qq={bot_qq}]'):#删除那些七七八八的触发指令
            msg = msg.replace(f'[CQ:at,qq={bot_qq}]','',1)
        else:
            msg = msg.replace('/AI','',1)
        lock = await get_user_lock(uid)
        async with lock:#异步锁，防串
            user_info = await user.load()#读取用户信息
            user_info['message'].append({'role':'user','content':msg})#直接把用户的对话加进去吧
            tsc = f"""好感总值：{user_info.get('favor')}\n好感总值范围:{love_up}~{-love_up}"""#提示词的附加板块
            logging.debug(f'{uid}提示词：{tsc}')
            try:
                logging.debug(f'{uid}读取人设')
                async with aiofiles.open(prompt_md,'r',encoding='utf-8') as f: #读取人设 是的我已经在编码上吃了一堆坑了
                    tsc = await f.read() + tsc
            except FileNotFoundError:#为了防止有某位人类手欠
                await send_msg('人设文件不存在，请检查文件名和文件存在情况',uid,gid)
                logging.exception('人设文件不存在，请检查文件名和文件存在情况')
                return {}
            message = [{'role':'system','content':tsc}] + user_info.get('message')


            logging.debug(f'{uid}发送了请求')
            openai_client = AsyncOpenAI(api_key=api_key,base_url=api_address)#构建AI客户端 APIKey或许也就在这里用了吧
            response = await openai_client.chat.completions.create(   #发送请求
                model=api_AI_model,#模型
                messages=message,#消息
                temperature=api_temperature,#温度，我个人习惯1.3
                max_tokens=api_max_tokens,#最大生成tokens，我个人习惯4096
                frequency_penalty=1,
                stream=False,
                response_format={
                    'type':'json_object'#确保必须是结构化输出
                }
            )
            logging.debug(f'{uid}请求已完成')
            try:
                s = json.loads(response.choices[0].message.content)#防止AI突然抽风不给我好的json
            except json.JSONDecodeError:
                if force_json:
                    logging.warning(f'{uid}的AI返回了非结构化数据，尝试强制解析')
                    try:
                        s = ast.literal_eval(response.choices[0].message.content)
                    except Exception:
                        await send_msg('强制解析出现错误，请联系管理员',uid,gid)
                        logging.exception(f'{uid}强制解析错误')
                        logging.error(response.choices[0].message.content)
                        return {}
                else:
                    await send_msg('解析出现错误，请联系管理员',uid,gid)
                    logging.exception(f'{uid}解析出现错误，真发生了?')
                    logging.error(response.choices[0].message.content)
                    return {}
            except Exception:
                await send_msg('解析出现错误，请联系管理员',uid,gid)
                #这种情况很少发生，不过为了输出的美观，还是不要在没结构化的情况下输出吧
                #不过懂点的朋友可以自行修改，毕竟这是我个人的喜好
                logging.exception(f'{uid}解析出现错误，真发生了?')
                logging.error(response.choices[0].message.content)
                return {}

            await send_msg(f'[CQ:at,qq={uid}] '+s.get('message'),uid,gid)#发送并at

            logging.debug(f'{uid}后处理')
            user_info['message'].append({'role':'assistant','content':str(s)})#录入
            user_info['time'].append(get_formatted_time())
            user_info['favor'] += s.get('favor')
            if len(user_info.get('message')) > message_up*2:#防超限，实际上它的限制对话是当前这个数字除二  #卧槽我差点忘了还要写0（到时候全删了是吧？？？）
                del user_info['message'][0]#删最早用户对话
                del user_info['message'][0]#删最早机器人对话
                del user_info['time'][0]#删最早时间记录
            if user_info.get('favor') > love_up:
                user_info['favor'] = love_up
            elif user_info.get('favor') < -love_up:
                user_info['favor'] = -love_up

            await user.write(user_info)#写入
            #如果这还报错你可以骂我了