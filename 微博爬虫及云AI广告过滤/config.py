import random


# 任务队列长度，0为不限制（注意过短的列队可能造成任务阻塞，无法继续执行，列队长度最好500以上）
Q_TASK_SIZE = 0  # 下载任务列队
Q_STORAGE_SIZE = 0  # 待存储任务列队
Q_REAULT_SIZE = 0  # 中间任务列队


# 各任务线程数
D_THREAD_NUM = 1  # 下载线程数
R_THREAD_NUM = 1  # 任务处理线程数
S_THREAD_NUM = 1  # 存储线程数


# 日志文件名
LOGFILE_NAME = 'runtimelog.log'


# oracle配置
WETHER_DB = False
ORACLE = {
    'user':'bq_data',
    'password':'tiger', 
    'host':'39.107.57.229:1521/orcl.lan',  # 正式爬取时应切换至229服务器内网ip
}  #链接配置
TABLE_NAME = 'temp'  # 当命令行传参没有数据表名时，默认的数据表名称
DATA_STRUCT = None  # 数据库中的数据结构


# 下载延时，针对单个线程
DELAY = 0
# 下载超时，针对每个下载任务
TIMEOUT = 2


# COOKIE可以是一个获取地址，或者一个python字典
# COOKIE = 'http://www.xcar.com.cn/bbs/header/bbsnav.htm?action=bbsnav&domain=club.xcar.com.cn&v=%s'
COOKIES = True
COOKIE = {
    '_T_WM': '89aca9ccbd77b1be331b3b3ac2227fe0',
    'SCF': 'Aj-Kmr1_7tff4BnQMB_KEUq2vHEeLgGPwpeMaSQrE5CNACkhn6ZIKI9A7Os5QWDtv1JEmN0uZ9OgVhW00kJjKos.',
    'SUB': '_2A25xHMcNDeRhGedG41IT-CrEwjiIHXVS_ulFrDV6PUJbkdAKLU_DkW1NUQ-5pR_LQpnoEJB3KMqciJf4kR0syHUT',
    'SUHB': '0oUpwYRBwarmuT',
    'TMPTOKEN': '1jnFGVbTeA9EaAr2Q4e2BAvpegg8bRD4SqCI68TuSLc2b8er2EQWVipEVI0A2mEm'
}


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


