1，.kjb文件为kettle的作业文件，包含了所有新闻爬虫的定时任务；

2，每个爬虫都是完整爬虫，都可独立运行；

3，增量任务依赖Redis作为缓存，迁移时需要将redis文件夹下的dump.rdb文件一同迁移。dump.rdb是redis的默认数据库文件，使用时放置在相应的redis根目录下即可；

4，单个爬虫的配置在每个爬虫的config.py文件中；

5，当页面解析规则改变时，只需改写page_parse.py文件。该文件下必须实现news_list_parse(response), news_info_parse(response, info_dict)。否则爬虫无发启动。

news_list_parse(response)函数接受一个相应对象，返回一个新闻列表的跟踪链接和一个新闻详情的链接列表，没有返回None, []
news_info_parse(response, info_dict)接受一个响应对象，一个详情字典，并在填充该字典后将其返回，否则返回空字典。