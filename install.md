# NapCat下载教程
首先，我知道这文档没啥用  
但是我知道有很多人都卡在下载这件破事上  
我们怎么能被区区Download和Install而卡住呢？？？  

## Windows
### 一键安装版
1. 在[NapCat的releases](https://github.com/NapNeko/NapCatQQ/releases/)中下载`NapCat.Shell.Windows.OneKey.zip`  
**一定要解压！一定要解压！一定要解压！**  
2. 然后双击`NapCatInstaller.exe`，等待下载  
3. 如果遇到在下载`NapCat.Shell.zip`时出现进度条一动不动，在最后出现一个`[成功] 文件下载完成: 0 MB`的话  
请在[github上直接下载`NapCat.Shell.zip`](https://github.com/NapNeko/NapCatQQ/releases/)并复制在与`NapCatInstaller.exe`相同的文件夹中(一定要覆盖)  
4. 等它跑完  
5. 双击进入`NapCat.一串数字.Shell`文件夹中
6. 双击`NapCatWinBootMain.exe`打开并扫码登录  

当然，你也可以在`napcat.quick.bat`中把它的`10086`改成你机器人的QQ号
### Shell版
1. 在[NapCat的releases](https://github.com/NapNeko/NapCatQQ/releases/)中下载`NapCat.Shell.zip`
2. **一定要解压！一定要解压！一定要解压！**  
3. 运行'launcher.bat'
    * 如果你是Win10，请运行`launcher-win10.bat`
4. 扫码登录

当然，你也可以在`quickLoginExample.bat`中把对应你系统的bat的前面的`REM`删除  
然后将`123456`替换为你机器人的QQ号

### Desktop版
在[NapCatQQ-Desktop的releases](https://github.com/NapNeko/NapCatQQ-Desktop/releases)中下载`msi`文件即可  
很抱歉，我没用过这个，我只过命令行版本的  
因此，我无法对这个的配置和安装起到任何的帮助，我只能告诉你这玩意很baka(笨蛋)  
因此如果你想用这个软件，请查看[NapCat文档](https://napneko.github.io/guide/boot/Shell)

## Linux
这里只说一键安装版本  
大佬请自行尝试其他方式
### 一键安装脚本
第一步，在root权限下(官方推荐非root)在Shell中输入下面这行命令(全部复制)
```bash
curl -o \
napcat.sh \
https://nclatest.znin.net/NapNeko/NapCat-Installer/main/script/install.sh \
&& bash napcat.sh
```  
第二步，等  
第三步，好了

# NapCat配置
NapCat配置的教程与Elaina配置的教程合并了  
请跳转至[配置文件详解](config_set.md)
