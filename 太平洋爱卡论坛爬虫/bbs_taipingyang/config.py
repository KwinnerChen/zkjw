import random


# 任务队列长度，0为不限制（注意过短的列队可能造成任务阻塞，无法继续执行，列队长度最好500以上）
Q_TASK_SIZE = 0  # 下载任务列队
Q_STORAGE_SIZE = 0  # 待存储任务列队
Q_REAULT_SIZE = 0  # 中间任务列队


# 各任务线程数
D_THREAD_NUM = 2  # 下载线程数
R_THREAD_NUM = 3  # 任务处理线程数
S_THREAD_NUM = 1  # 存储线程数


# 日志文件名
LOGFILE_NAME = 'runtimelog.log'


# oracle配置
ORACLE = {
    'user':'bq_data',
    'password':'tiger', 
    'host':'39.107.57.229:1521/orcl.lan',  # 正式爬取时应切换至229服务器内网ip
}  #链接配置
TABLE_NAME = 'CRAW_BBS_CAR'  # 当命令行传参没有数据表名时，默认的数据表名称
DATA_STRUCT = {
    "JMETABBSID": 'NUMBER(20) NULL',
    "CRUSER" :'VARCHAR2(255 BYTE) NULL' , 
    "CRTIME": 'DATE NULL' ,
    "CRNUMBER": 'NUMBER(20) NULL' ,
    "DOCCHANNELID": 'NUMBER(20) NULL' ,
    "DOCSTATUS": 'NUMBER(2) NULL' ,
    "SINGLETEMPKATE": 'NUMBER(20) NULL' ,
    "SITEID": 'NUMBER(20) NULL' ,
    "DOCVALID": 'DATE NULL' ,
    "DOCPUBTIME": 'DATE NULL' ,
    "OPERUSER": 'VARCHAR2(255 BYTE) NULL' ,
    "OPERTIME": 'DATE NULL' ,
    "DOCTITLE": 'VARCHAR2(255 BYTE) NULL' ,
    "DOCRELTIME": 'DATE NULL' ,
    "BBS_ID": 'NUMBER(20) NULL' ,
    "BBS_BT": 'VARCHAR2(4000 BYTE) NULL' ,
    "BBS_QA": 'VARCHAR2(2000 BYTE) NULL' ,
    "BBS_JING": 'VARCHAR2(2000 BYTE) NULL' , 
    "BBS_NR": 'CLOB NULL' , 
    "BBS_SF": 'VARCHAR2(2000 BYTE) NULL' ,
    "BBS_DS": 'VARCHAR2(2000 BYTE) NULL' ,
    "BBS_FTSJ": 'VARCHAR2(70) NULL' ,
    "BBS_HFS": 'VARCHAR2(2000 BYTE) NULL' , 
    "BBS_DJS": 'VARCHAR2(2000 BYTE) NULL' , 
    "BBS_YHID": 'VARCHAR2(2000 BYTE) NULL' ,
    "BBS_ZCRQ": 'VARCHAR2(2000 BYTE) NULL' ,
    "BBS_TABLENAME": 'VARCHAR2(2000 BYTE) NULL' , 
    "BBS_CX": 'VARCHAR2(200 BYTE) NULL' , 
    "BBS_CXFL": 'VARCHAR2(2000 BYTE) NULL' ,
    "KEYWORD333": 'VARCHAR2(200 BYTE) NULL' ,
    "KEYWORD": 'CLOB NULL' , 
    "ADJECTELATION111": 'VARCHAR2(2000 BYTE) NULL' ,
    "T1": 'CLOB NULL' ,
    "T2": 'CLOB NULL' ,
    "T3": 'CLOB NULL' ,
    "T4": 'CLOB NULL' ,
    "PRICES": 'VARCHAR2(500 BYTE) NULL' , 
    "BRAND": 'VARCHAR2(500 BYTE) NULL' , 
    "SATISFIED": 'NUMBER NULL' , 
    "NEUTRAL": 'NUMBER NULL' ,
    "UNSATISFY": 'NUMBER NULL' ,
    "CT_ADJ": 'CLOB NULL' ,
    "CUTPARTIME": 'DATE NULL' ,
    "CUTSENTIME": 'DATE NULL' ,
    "ADJECTELATION": 'CLOB NULL' ,
    "KEYWORDTIME": 'DATE NULL' ,
    "ADJ_STARTS": 'NUMBER(10) NULL' ,
    "CUT_STATUS": 'NUMBER(10) NULL' ,
    "CT_STOPWORD": 'CLOB NULL' ,
    "BBS_SHSJ": 'DATE NULL' ,
    "KEYTONGYICI": 'VARCHAR2(2000 BYTE) NULL' ,
    "KEYRELATION": 'VARCHAR2(2000 BYTE) NULL' ,
    "KEY_MIN": 'NUMBER NULL' ,
    "KEY_MAX": 'NUMBER NULL' ,
    "KEYNUM": 'NUMBER NULL' ,
    "SOURCE": 'VARCHAR2(2000 BYTE) NULL' ,
    "FORM_NR": 'CLOB NULL' ,
    "CLASSIFY": 'VARCHAR2(2000 BYTE) NULL' ,
    "NRLEN": 'NUMBER NULL' ,
    "KEYWORD_CT": 'VARCHAR2(200 BYTE) NULL' ,
    "KEYWORD_CX": 'VARCHAR2(200 BYTE) NULL' ,
    "BBS_IMG": 'CLOB NULL' ,
    "BBS_YHM": 'VARCHAR2(2000 BYTE) NULL' ,
    "BBS_NEWORUP": 'VARCHAR2(255 BYTE) NULL' ,
    "BBS_ANALYSIS": 'VARCHAR2(255 BYTE) NULL' ,
    "CRAW_TIME": 'DATE NULL' , 
    "BBS_ACHGZ": 'VARCHAR2(500 BYTE) NULL' ,
    "BBS_JHS": 'VARCHAR2(255 BYTE) NULL' , 
    "BBS_FTZS": 'VARCHAR2(255 BYTE) NULL' ,
    "BBS_HQTTS": 'VARCHAR2(255 BYTE) NULL' , 
}  # 数据库中的数据结构


# 下载延时，针对单个线程
DELAY = 0.5
# 下载超时，针对每个下载任务
TIMEOUT = 2


# COOKIE获取地址, 是一个随时间变化的地址，末尾为当前时间格式如：201811291833
# URL_FOR_COOKIE = 'http://www.xcar.com.cn/bbs/header/bbsnav.htm?action=bbsnav&domain=club.xcar.com.cn&v=%s'


# 爬虫模块, 所有的爬虫模块都要在此注册
SPIDERS = [
    'spider.AuDiSpider',
    'spider.SchnitzerSpider',
    'spider.ALPINASpider',
    'spider.ARCFOXSpider',
    'spider.AlfaRomeoSpider',
    'spider.AstonMartinSpider',
    'spider.AiChiSpider',
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


# cartype获取服务器
# CARTYPE = {
#     'user':'bq_data',
#     'password':'tiger',
#     'host':'39.107.57.229：1521/orcl.lan'  # 正式爬取时应改成内网ip
# }
# CARTYPE_TABLE_NAME = 'TABLENAME_PRICES_BRAND'
