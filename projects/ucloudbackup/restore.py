import os
def find_deep_path(current):
    for _ in range(4):
        for lists in os.listdir(current): 
            path = os.path.join(current, lists)
            if os.path.isdir(path):
                current = path
                break
    return current


def restore():
    current = '/data/monitor/check'
    print current
    deep_dir = find_deep_path(current)
    print deep_dir
    os.system('mongorestore -d today {}/db_cache/'.format(deep_dir))
    os.system('mongorestore -d today {}/db_log/'.format(deep_dir))
    os.system('mongorestore -d today {}/db_ruyi/'.format(deep_dir))
    os.system('mongorestore -d today {}/db_wechat/'.format(deep_dir))
    os.system('mongorestore -d today {}/test/ '.format(deep_dir))
