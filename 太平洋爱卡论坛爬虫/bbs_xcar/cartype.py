#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


from storage import Oracle


def get_cartype_dict(user, password, host, table_name):
    '''
    用于从数据库中获取车型，车商字典
    '''
    orc = Oracle(user, password, host)
    data = orc.getall(table_name)
    orc.close()
    return data


if __name__ == '__main__':
    import os
    os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
    data = get_cartype_dict('bq_data', 'tiger', '39.107.57.229:1521/orcl.lan', 'TABLENAME_PRICES_BRAND')
    print('奥迪A3' in data)
