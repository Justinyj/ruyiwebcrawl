import os
def go(current, level):
    if level == 4:
        return current
    for lists in os.listdir(current): 
        path = os.path.join(current, lists)
        if os.path.isdir(path):
            return go(path, level+1)


def restore():
    current = '/data/monitor/check'
    print current
    deep_dir = go(current, 0)
    print deep_dir
    os.system(('mongorestore -d today "{}"/db_cache/').format(deep_dir))
    os.system(('mongorestore -d today "{}"/db_log/').format(deep_dir))
    os.system(('mongorestore -d today "{}"/db_ruyi/').format(deep_dir))
    os.system(('mongorestore -d today "{}"/db_wechat/').format(deep_dir))
    os.system(('mongorestore -d today "{}"/test/ ').format(deep_dir))
