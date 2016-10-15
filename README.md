# FTPDownload
一个服务需要先下载大资源的FTP工具，这个服务是放在docker中的，将这个FTP下载工具也放在另外一个docker中，在kubernetes中启动这个服务容器前先init这个FTP下载容器

## 项目结构
	FTPDownload
	├── down-resource
	│   ├── Dockerfile //将这个项目built成docker镜像的Dockerfile
	│   ├── FTPDownload.py  //多线程下载多个文件，并且有下载选项
	│   ├── down_file.py //下载单个文件
	│   └── md5sum.py //计算大文件的MD5值
	└── guestbook-controller.json //kubernetes中服务先下载文件的RC文件
	
