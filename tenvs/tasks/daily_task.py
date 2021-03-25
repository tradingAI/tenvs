import numpy as np
from numpy.random import default_rng


class DailyTask:
    codes = []
    code_num = 0
    window_size = 1
    feature_num = 1
    n_step = 0
    current_step = 0
    timestamps = []
    # 开市=1，休市=0
    status = None  # np.array([n_step, code_num])
    # 开盘价
    opens = None  # np.array([n_step, code_num])
    # 收盘价
    closes = None  # np.array([n_step, code_num])
    # 最高价
    highs = None  # np.array([n_step, code_num])
    # 最低价
    lows = None  # np.array([n_step, code_num])
    # 前一收盘价
    precloses = None  # np.array([n_step, code_num])
    # 复权因子
    adjusts = None  # np.array([n_step, code_num])
    features = None  # np.array([n_step, code_num, window_size, feature_num])


class RandomDailyTask(DailyTask):
    codes = ['000001.SZ']
    code_num = 1
    window_size = 10
    feature_num = 3
    n_step = 10
    timestamps = [i for i in range(20)]
    status = np.ones(shape=(n_step, code_num))
    preclose = np.ones(shape=(n_step, code_num)) * 10
    rng = default_rng(0)
    closes = rng.standard_normal(size=(n_step, code_num)) + 10.0
    opens = closes + rng.standard_normal(size=(n_step, code_num))
    highs = closes + rng.standard_normal(size=(n_step, code_num))
    lows = closes - rng.standard_normal(size=(n_step, code_num))
    features = rng.standard_normal(
        size=(n_step, code_num, window_size, feature_num))
