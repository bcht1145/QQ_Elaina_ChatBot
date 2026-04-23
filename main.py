from config import *
from user_json import *
from openai import OpenAI,AsyncOpenAI
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
    logging.warning('数据库不存在，创建')
    os.makedirs(os.path.join(path,'user_json'))

server = FastAPI(title='Elaina')
client_version = 'v1.1.0'# 机器人版本，用于OTA，不要修改
file_lock = asyncio.Lock() #谁持锁，这文件就是谁的天下。函数啊，大文件…就给你了…(趋势)(大清就交给你了)
user_locks = {}  # 存储每个用户的锁

def get_formatted_time():
    """返回当前时间，格式为 '年份-月份-日期-小时:分钟:秒'"""
    return datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

def hot_reload_config():
    """用于热重载配置文件"""
    logging.info('正在热重载配置文件')
    importlib.reload(config)
    globals().update({k: v for k, v in vars(config).items() if not k.startswith("_")})
    """
    我承认这一大堆我也看不懂
    反正就是把那一大堆变量读进来,赋值给全局变量
    并且忽视私有变量(下划线开头)
    """

async def get_user_lock(uid: int):
    """获取用户专属的异步锁"""
    async with file_lock:
        if uid not in user_locks:
            user_locks[uid] = asyncio.Lock()
        return user_locks[uid]

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

@server.post('/')
async def auto_reply_message(data: dict):
    uid = data.get("user_id")#目标qq
    gid = data.get("group_id")#群聊qq
    mid = data.get("message_id")#消息编号
    msg = data.get("raw_message")#消息

    if msg is not None and (msg[0]=='/' or msg.startswith(f'[CQ:at,qq={bot_qq}]')):#若消息不为空，且开头为斜杠或at的情况下受理
        msg = msg.replace("&#91;", "[").replace("&#93;", "]").replace("&amp;", "&").replace("&#44;", ",")#转码
        if uid==2854196310:#这里是防Q群管家
            logging.debug('Q群管家at你了')
            return {}
        #加载json用户信息
        user = User(uid,path)

        if msg == '/help':#用于获取帮助
            try:
                with open('help.txt','r',encoding='utf-8') as f:#防手欠x2
                    await send_msg(f'{f.read()}',uid,gid)
            except FileNotFoundError:
                await send_msg('未找到帮助文档文件',uid,gid)
                logging.exception('未找到帮助文档文件，请确认help.txt是否存在且未重命名')
                return {}
            return {}

        if msg == '/重载' and uid in admin:
            hot_reload_config()
            await send_msg('已重载配置文件',uid,gid)

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
    return {}

if __name__ == '__main__':#但愿没人闲的没事把这玩意当模块跑
    logging.info(f'当前版本:{client_version}')
    if OTA_allow:
        logging.info('正在检查更新...')
        success, msg = ota.ota_update(client_version, github_repo, auto_restart=True)
        logging.info(msg)
        
    uvicorn.run(server,host=client_address,port=client_port)#每日禁用debug(1/1)
