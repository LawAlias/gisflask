# gisflask
Web GIS framework based on flask（使用flask搭建的webgis框架）
长期更新中，欢迎关注
![Alt Text](https://ws4.sinaimg.cn/large/006tKfTcly1g1agsxb82yj31p00u0k02.jpg)
#一、环境搭建：
##1.1 数据库：
本系统采用安装了postgis扩展的postgresql数据库（或其他支持地理空间数据扩展的数据库）,使用之前需要在main/setting.py文件中修改连接字符：
![Alt Text](https://ws3.sinaimg.cn/large/006tKfTcly1g1ah6cuir8j31q806yq65.jpg)
##1.2 python环境为python2.x
#二、数据初始化：
因为使用了flask的虚拟环境，所以首先使用vs code打开该文件夹，在命令资源符中打开后，依次输入：
pipenv install
pipenv shell
flask initdb//初始化数据库表
flask initdata//初始化数据
flask run
即可启动

#三、部分功能截图
待有时间慢慢完善该文档，在这就先贴上截图：
![Alt Text](https://ws2.sinaimg.cn/large/006tKfTcly1g1ahjx55r1j31o60re0zu.jpg)
![Alt Text](https://ws1.sinaimg.cn/large/006tKfTcly1g1ahkpoxjkj31qh0u07d6.jpg)
目前上传支持shp和kml
![Alt Text](https://ws2.sinaimg.cn/large/006tKfTcly1g1ahxiws9ij31s90u0gp6.jpg)
![Alt Text](https://ws3.sinaimg.cn/large/006tKfTcly1g1ahz9u4j8j31z20r6n10.jpg)
权限管理：
![Alt Text](https://ws3.sinaimg.cn/large/006tKfTcly1g1ahzwcdn0j31l60u0grw.jpg)
![Alt Text](https://ws1.sinaimg.cn/large/006tKfTcly1g1ai059u4ij31no0u00w5.jpg)








