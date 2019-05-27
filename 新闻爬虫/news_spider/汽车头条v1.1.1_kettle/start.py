#! usr/bin/env python3
# -*- coding: utf-8 -*-


from task_manager_server import get_queue
import config


def start():
    q = get_queue((config.TASK_KEY['host'], config.TASK_KEY['port']), authkey=config.TASK_KEY['authorkey'])
    task_url = config.START_URL
    if isinstance(task_url, (list, tuple)):
        for u in task_url:
            q.put(u)
    elif isinstance(task_url, str):
        q.put(task_url)

if __name__ == '__main__':
    start()