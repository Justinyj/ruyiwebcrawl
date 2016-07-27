### length
是一个估计值，length(倍数) = 需要爬取所有URL / 配置文件url初始化时插入redis产生队列长度
第一级目录length为1，一个上级目录产生的下级目录数依次为N2, N3…  length=1+N2+N3
