import httpx
import logging

logging.getLogger(__name__)#同步主文件的日志格式

async def send_http_post(url:str,data:dict,try_limit:int=5) -> None:
    """
    优雅,封装,自处理错误,自重试的http请求  
    传入:  
    url -> 请求的url  
    data -> post的数据  
    try_limit -> 重试次数(可选)(默认5次)  
    返回:  
    None  
    """
    for i in range(try_limit):#自动重试
        try:
            async with httpx.AsyncClient() as client:#使用异步调用post
                response = await client.post(url,json=data,timeout=5)
                if response.is_success:
                    logging.debug('httpx发送请求成功')
                    return
        except httpx.ConnectTimeout:#处理超时
            logging.warning('httpx发送请求超时,重试中...')
        except httpx.HTTPStatusError:
            logging.exception('http错误')
            break #不重试
        except Exception:
            logging.exception('httpx发送出现错误')

async def http_download(url:str,data:dict,try_limit:int=5):
    """
    优雅,封装,自处理错误,自重试的http下载  
    需要注意的是,请自行根据返回的数据类型自行处理数据  
    传入:  
    url -> 请求的url  
    data -> post的数据  
    try_limit -> 重试次数(可选)(默认5次)  
    返回:  
    依照你所请求的数据类型返回
    """
    for i in range(try_limit):#自动重试
        try:
            async with httpx.AsyncClient() as client:#使用异步调用post
                response = await client.post(url,json=data,timeout=5)
                if response.is_success:
                    content_type = response.headers.get('Content-Type','').lower()#将所有的内容类型都转为小写，方便判断
                    if 'application/json' in content_type:#若是json，则自动解析，由于是底层，因此不允许使用高级json解析器
                        return response.json()
                    elif 'text/plain' in content_type:#纯文本就返回吧
                        return response.text
                    elif 'image/' in content_type or 'application/octet-stream' in content_type:#如果是二进制数据则返回bytes
                        return response.content
                    else:
                        logging.warning(f'未知的Content-Type:{content_type}')#统一返回，总不可能返回response对象吧？
                        return response.content
                    
        except httpx.ConnectTimeout:
            logging.warning('http下载超时,重试中...')
        except httpx.HTTPStatusError:
            logging.exception('http错误')
            break #不重试
        except Exception:
            logging.exception('httpx下载出现错误')
