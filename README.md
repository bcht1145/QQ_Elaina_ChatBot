# Elaina ChatBot
一个使用Python开发的QQ AI聊天机器人  
支持大部分语言模型，使用OpenAI作为框架和协议进行通信  

### 待实现功能
- [ ] 聊天功能
    - [x] 聊天功能
    - [ ] 图片识别  
- [ ] 用户数据管理
    - [x] JSON文件存储
    - [ ] MySQL数据库存储
- [ ] 杂项
    - [ ] OTA更新

# 部署方法
## QQ Server
我们强烈推荐使用[**NapCat**](https://github.com/NapNeko/NapCatQQ)作为QQ服务端进行使用  
具体部署方法请查看[NapCat文档](https://napneko.github.io/)，或者直接看我的[NapCat大白话手把手教你部署](install.md)  
下面的所有教程均将使用NapCat作为QQ服务端

## Elaina Client
### Download
一般情况下，下载本文件有两个办法  
1. 右上角点`Code`，点击`Download ZIP`。然后等待就行
2. 使用git  
随便找个文件夹，在该文件夹内打开终端，输入下面的一大长串就可以下载了
```Bash
git clone https://github.com/bcht1145/QQ_Elaina_ChatBot.git
```  

### Config
在开始正式运行前，请保证配置文件`config.py`已配置好  
你可以自由的修改其中的内容，前提你需要知道他们都代表着什么  
你可以阅读[配置文件详解](config_set.md)来进行配置

### QQ Run
终于开始跑了吗！太好了！  
不过先别急着运行`main.py`，请先把你的QQ端启动好  
#### Windows端
##### OneKey用户
进入`NapCat.一堆数字.Shell`，双击运行`napcat.quick.bat`即可
##### Shell用户
请到达你的NapCat目录，运行`launcher.bat`，并扫码登录  
如果你是Win10用户，请使用`launcher-win10.bat`  
或者你要是图省事，也可以在`quickLoginExample.bat`中，将命令中的`REM`删除并在前面的bat运行文件前替换为Bot的QQ号

#### Linux端
如果你使用了我所推荐的**Linux一键使用脚本**,那么直接在shell里输入`napcat`即可  
* 可视化界面：最简单的一个，在配置完成之后直接就可以扫码运行  
如手机并未显示登录成功，请查看日志并扫码登录，然后按`q`键退出日志界面
* 命令行界面：输入`napcat start 机器人QQ号`即可  
如手机并未显示登录成功，请查看日志并扫码登录，然后按`Ctrl + C`键退出日志界面

### Elaina Run
终于到了Bot运行的时候  
在Elaina的根目录下，在Shell中运行下面的命令即可  
```Bash
python main.py
```

# 许可证
Apache 2.0 | © 2026 bcht
See LICENSE for details.
