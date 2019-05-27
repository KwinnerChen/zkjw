import random


# 任务队列长度，0为不限制（注意过短的列队可能造成任务阻塞，无法继续执行，列队长度最好1000以上）
Q_TASK_SIZE = 0  # 下载任务列队
Q_STORAGE_SIZE = 0  # 待存储任务列队
Q_REAULT_SIZE = 0  # 中间任务列队


# 各任务线程数
D_THREAD_NUM = 1  # 下载线程数
R_THREAD_NUM = 1  # 任务处理线程数
S_THREAD_NUM = 1  # 存储线程数


# 日志文件名
LOGFILE_NAME = 'runtimelog.log'


# 数据库配置支持oracle和mysql
WETHER_DB = False
DBNAME = 'mysql'
LINK = {
    'user':'root',
    'password':'tiger', 
    'host':'47.93.151.74',
    'port':3306,
    'db':'zkjw',
}  #链接配置，注意mysql和oracle的配置的不同
TABLE_NAME = 'TABLE_NAME'  # 当命令行传参没有数据表名时，默认的数据表名称
DATA_STRUCT = None  # 数据库中的数据结构，mysql可以设为None，oracle是必须的


# 下载延时，针对单个线程
DELAY = 1
# 下载超时，针对每个下载任务
TIMEOUT = 2


# COOKIE可以是一个字符串用于获取cookie的地址，或者一个cookie的字典
COOKIES = False
COOKIE = {}


# 爬虫模块, 所有的爬虫模块都要在此注册
SPIDERS = [
    'spider.Spider',
    ]


# 任务列队的发布地址和口令
TASK_KEY = {
    'addr':'localhost',
    'port':random.randint(8000, 65000),
    'authkey':b'k',
}


# IPPool服务器
WETHER_PROXY = False
PROXY = {
    'user':'beiqi',
    'password':'beiqi',
    'host':'123.57.7.118:1521/orcl',
}
PROXY_TABLE_NAME = 'PROXIES'


# 用户代理池
WETHER_UAPOOL = False

