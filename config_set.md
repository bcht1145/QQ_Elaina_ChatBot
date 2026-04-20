# NapCat服务端配置教程
我们强烈建议你使用WebUI配置NapCat  
### WebUI
在运行时，进入日志可以看到形如`[info] [NapCat] [WebUi] WebUi User Panel Url: http://127.0.0.1:6099/webui?token=xxxxx`的信息，使用该网址进行访问  
Linux端也可以打开`/opt/QQ/resources/app/app_launcher/napcat/config/webui.json`文件，**前提是你是通过一键安装脚本安装的**  
如果你是在服务器上部署的，请将`127.0.0.1`替换为你服务器的内网或外网ip地址

1. 进入WebUI，选择左边的`网络配置`  
2. 选择左上角的`新建`
3. 创建两个配置，分别为`HTTP服务器`和`HTTP客户端`
4. `HTTP服务器`输入机器人config.py中的`client_address`和`client_port`  
    * 以`http://client_address:client_port`的格式去输入  
    * 若你还没有配置机器人，则推荐使用`127.0.0.1`作为地址，`3000`作为端口  
    * 或者你明白如何配置可以略过我的建议
5. `HTTP客户端`输入机器人config.py中的`server_address`
    * 将`server_address`中的`ip`和`port`的格式去填
    * `ip`对应`主机`,`port`对应`端口`
    * 若你还没有配置机器人，则推荐使用`http://127.0.0.1:3001`(请不要在NapCat的配置中输入`http://`和`:`)
    * 或者你明白如何配置可以略过我的建议

### 文件
大佬请移步至[NapCat文档](https://napneko.github.io/config/basic)  
小白非常**不建议**使用该配置方法  

# Elaina config.py文件配置教程
我已经尽量用普通人能听得懂的方式去说了  
大佬几乎可以不用看这些  
哎不对，会有大佬关注这个项目吗？

### 注意事项
除非你有其他需求，或者你知道你在做什么的情况下  
否则我们不建议你将`ip`设置为除`127.0.0.1`以外的ip  
所有的引号不应被移除，所有没有引号的地方均不应加入引号  
请不要删除`admin`中的中括号(列表)，除非管理就你一个……

## 通信配置
### server_address
格式为:
```py
'http://ip:port'
```
该变量与NapCat配置中的`httpServer`对应  
* `ip`对应`主机`  
* `port`对应`端口`  

请不要修改除`ip`和`port`的其他部分

### client_address和client_port
对应着NapCat配置中的`httpClient`部分  
NapCat配置中的`httpClient`与`'http://ip:port'`相似  
因此  
* `client_address`对应`ip`
* `client_port`对应`port`

## AI配置
### api_key
你所使用的AI的厂商所为你派发的Key  
通常情况下，直接复制进来即可

### api_address
你所使用的AI的厂商的服务地址  
注意是API地址，不要把浏览器上的网址复制进来！  
通常情况下，厂商的文档中均会提到API地址  
需要注意的是，请使用与OpenAI兼容的地址

### api_AI_model
你所使用的AI的厂商的模型  
通常情况下，厂商的文档里应该有AI的名字，直接复制即可

### api_temperature和api_max_tokens
如果没有特殊需要，保留不动即可  
在修改前，请你清楚你在做什么，或是你了解这两个变量的用途

## 机器人配置
### OTA_allow
OTA开关，目前正在更新中，你开了也没用……

### github_repo
OTA仓库的地址，**不要修改！！！**  
除非你知道你在做什么…

### bot_qq
机器人的QQ号，传入纯数字即可

### admin
管理员的QQ号  
如需多名管理员，请使用英文逗号分割，每个空隙传入QQ号

### force_json
在常规解析频频失效的情况下，尝试强制解析  
通常情况下，此项固定为`False`(关)  
如你发现常规解析频频出错，请将其改为`True`(开)尝试  
如还是出错，请向本项目提交Issues，并附上日志  
**前提是你已经尝试过将`force_json`改为`True`**

### prompt_md
AI提示词的文件名  
需要有后缀名，允许md文件和txt文件  
如需将其迁移至别处，则请输入绝对路径  
本提示词可以随便改，但是**请保留:**
* 好感度系统
* 输出要求
* 外界信息

**这很重要！**  
不然，Elaina的AI可能会傻，然后静静报个错

## 杂项
### message_up
用户与机器人对话的回合上线数  
超过该上线的会删除最老的信息  
如需无限聊天，可以写入一个超级大的数字  
当然，除非你不心疼你的钱包……

### love_up
好感度系统  
机器人对你的好感度上限和下限为你所设置的`love_up`~`-love_up`  
需要注意的是，只能传入一个**正整数**
