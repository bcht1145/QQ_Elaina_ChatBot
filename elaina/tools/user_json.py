import json
import os
import logging
import asyncio
import aiofiles
#主要使用json文件进行处理
#MySQL?在编了在编了

from elaina.common.path import ROOT_PATH

logging.getLogger(__name__)#同步主文件的日志格式

user_template = {#用户文件模版
    "message":[],#消息，包括用户和机器人的
    "favor":0,#好感度
    "time":[]
}

def is_user_template_complete(data : dict ) -> bool:#用于检查传入的字典是否符合规范
    """
    输入  
    data->dict  
    输出  
    bool  
    用于检查用户信息是否符合模版，返回True表示符合模版，返回False表示不符合模版  
    防呆不防傻，只要我不傻，并且用这个，估计就没毛病  
    """
    # 必需键集合
    required_keys = {"message", "favor", "time"}
    # 检查键是否存在
    if not all(key in data for key in required_keys):
        return False
    # 检查值的类型
    type_checks = {
        "message": list,
        "favor": int,
        "time": list
    }
    for key, expected_type in type_checks.items():#挨个检查  #将样本转换为可遍历的类型
        if not isinstance(data[key], expected_type):#判断是否为当前的类型
            return False
    return True

class User:
    def __init__(self,uid):#初始化
        self.uid = uid
        self._path = os.path.join(ROOT_PATH,'user_json',str(self.uid)+'.json')
    
    async def load(self) -> dict:
        """若存在用户文件，则返回用户的信息  
        若不存在，则返回初始模版并创建  
        输入:  
        None  
        输出:  
        dict -> 用户信息  
        模版:  
        "message":[],#消息，包括用户和机器人的  
        "favor":0,#好感度  
        "time":[]"""  
        user = {}
        if os.path.isfile(self._path):
            async with aiofiles.open(self._path,'r',encoding='utf-8') as f:
                user = json.loads(await f.read())
        else:
            async with aiofiles.open(self._path,'w',encoding='utf-8') as f:
                await f.write(json.dumps(user_template,ensure_ascii=False,indent=4))
                user = user_template
        return user
    
    async def delete(self) -> None:
        """重置用户文件，什么都不返回  
        输入:  
        None  
        输出:  
        None"""
        async with aiofiles.open(self._path,'w',encoding='utf-8') as f:
            await f.write(json.dumps(user_template,ensure_ascii=False,indent=4))

    async def write(self,data) -> None:
        """将用户信息写入文件  
        传入:
        data -> dict
        输出:  
        None  
        注意，别传入一个不是字典的玩意  
        不要让我在修bug的时候看到这玩意报错!!!"""
        if not is_user_template_complete(data):#我不管，就算我提醒了我也要做个防备措施
            logging.error(f'{self.uid}模版不匹配！')
            raise ValueError('模版不匹配！李在干什麽？')
            return #我知道这行没意义，但是我就是习惯了
        
        async with aiofiles.open(self._path,'w',encoding='utf-8') as f:
            await f.write(json.dumps(data,ensure_ascii=False,indent=4))
    
if __name__ == '__main__':
    print('我还是很好奇，你运行这个干啥')
