import os
import pickle


def save_task(t, tpath):
    # NOTE(liuwen): 目录需要提前创建
    dir = os.path.dirname(tpath)
    if not os.path.exists(dir):
        os.makedirs(dir)
    with open(tpath, 'wb') as f:
        pickle.dump(t, f)


def load_task(tpath):
    # NOTE(liuwen): tpath 必需存在
    t = None
    with open(tpath, 'rb') as f:
        t = pickle.load(f)
    return t
