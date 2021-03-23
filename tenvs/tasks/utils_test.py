import random
import sys

import numpy as np
import pytest
from numpy.random import default_rng
from tenvs.tasks.daily_task import RandomDailyTask
from tenvs.tasks.utils import load_task, save_task


def test_save_and_load():
    rng = default_rng(0)
    a = rng.random(size=(5,))
    assert np.mean(a) == 0.3555039599500642
    tpath = '/tmp/tenvs/test/random.pkl'
    task = RandomDailyTask()
    assert task.codes == ['000001.SZ']
    assert np.sum(np.mean(task.closes)) == 10.084679810855311
    save_task(task, tpath)
    new_task = load_task(tpath)
    assert np.array_equal(task.features, new_task.features)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
