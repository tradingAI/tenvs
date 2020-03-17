# -*- coding:utf-8 -*-

import datetime
import logging
import os
import random
import unittest

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

from tenvs.envs.multi_vol import MultiVolEnv
from tenvs.market import Market

logging.root.setLevel(logging.INFO)
register_matplotlib_converters()


class TestMultiVol(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # NOTE: 需要在环境变量中设置 TUSHARE_TOKEN
        ts_token = os.getenv("TUSHARE_TOKEN")
        self.start = "20190101"
        self.end = "20200101"
        self.codes = ["000001.SZ", "000002.SZ"]
        # self.indexs = ["000001.SH", "399001.SZ"]
        self.indexs = []
        self.show_plot = False
        # self.indexs = []
        self.data_dir = "/tmp/tenvs"
        self.m = Market(
            ts_token=ts_token,
            start=self.start,
            end=self.end,
            codes=self.codes,
            indexs=self.indexs,
            data_dir=self.data_dir)
        self.invesment = 100000.0
        self.look_back_days = 10
        self.env = MultiVolEnv(
            self.m,
            investment=self.invesment,
            look_back_days=self.look_back_days)

    def plot_portfolio_value(self, name):
        plt.figure(figsize=(15, 7))
        MTFmt = '%Y%m%d'
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter(MTFmt))
        plt.title(name, fontsize=10)
        dates = [datetime.datetime.strptime(d, MTFmt) for d in self.env.dates[
            self.look_back_days:]]
        plt.plot(dates,
                 self.env.portfolio_value_logs,
                 label="portfolio_value")
        plt.show()

    def test_get_open_dates(self):
        self.assertEqual(244, len(self.env.dates))

    def test_buy_and_hold(self):
        self.env.reset()
        action = self.env.get_buy_close_action(datestr=self.env.current_date)
        obs, reward, done, info, _ = self.env.step(action, only_update=False)
        action = [0] * 4
        while not done:
            # buy and hold, 持仓不动
            _, _, done, _, _ = self.env.step(action, only_update=True)
        self.assertEqual(144057.17, self.env.portfolio_value)
        if self.show_plot:
            self.plot_portfolio_value("buy_and_hold")

    def test_random(self):
        # logging.root.setLevel(logging.DEBUG)
        random.seed(0)
        self.env.reset()
        action = self.env.get_buy_close_action(datestr=self.env.current_date)
        obs, reward, done, info, _ = self.env.step(action, only_update=False)
        while not done:
            # buy and hold, 持仓不动
            action = self.env.get_random_action()
            _, _, done, _, _ = self.env.step(action, only_update=False)
        self.assertEqual(119229.0, round(self.env.portfolio_value, 1))
        if self.show_plot:
            self.plot_portfolio_value("random_action")

    def test_static(self):
        self.env.reset()
        action = self.env.get_buy_close_action(datestr=self.env.current_date)
        obs, reward, done, info, _ = self.env.step(action, only_update=False)
        action = [0.1, -1, -0.1, 0, 0.1, -1, -0.1, 0]
        while not done:
            _, _, done, _, _ = self.env.step(action, only_update=False)
        self.assertEqual(104933, int(self.env.portfolio_value))
        if self.show_plot:
            self.plot_portfolio_value("static")

    def test_get_buy_close_action(self):
        actual = self.env.get_buy_close_action(datestr='20190116')
        expect = [0, -1, 0.23438, 0, 0, -1, 0.10334000000000002, 0]
        self.assertEqual(expect, actual)


if __name__ == '__main__':
    unittest.main()
