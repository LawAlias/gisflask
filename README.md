一、环境搭建：

1.1 数据库：

本系统采用安装了postgis扩展的postgresql数据库（或其他支持地理空间数据扩展的数据库）,使用之前需要在main/setting.py文件中修改连接字符：


1.2 python环境为python2.x

二、数据初始化：

因为使用了flask的虚拟环境，所以首先使用vs code打开该文件夹，在命令资源符中打开后，依次输入：

pipenv install

pipenv shell

flask initdb//初始化数据库表

flask initdata//初始化数据

flask run

即可启动

三、部分功能截图

待有时间慢慢完善该文档，在这就先贴上截图：



目前上传支持shp和kml



权限管理：










