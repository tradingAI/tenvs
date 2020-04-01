# -*- coding:utf-8 -*-

import logging
import os
import unittest

from tenvs.market import Market

logging.root.setLevel(logging.ERROR)


class TestMarket(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # NOTE: 需要在环境变量中设置 TUSHARE_TOKEN
        ts_token = os.getenv("TUSHARE_TOKEN")
        self.start = "20190101"
        self.end = "20200101"
        self.codes = ["000001.SZ"]
        self.indexs = ["000001.SH", "399001.SZ"]
        # self.indexs = []
        self.data_dir = "/tmp/market"
        self.m = Market(
            ts_token=ts_token,
            start=self.start,
            end=self.end,
            codes=self.codes,
            indexs=self.indexs,
            data_dir=self.data_dir)

    def test_init_codes_history(self):
        self.assertEqual(244, len(self.m.indexs_history["000001.SH"]))
        self.assertEqual(244, len(self.m.codes_history[self.codes[0]]))

    def test_init_size_info(self):
        self.assertEqual(10, self.m.equity_hfq_info_size)
        self.assertEqual(18, self.m.indexs_info_size)

    def test_is_suspended(self):
        self.assertTrue(self.m.is_suspended(code='000', datestr=''))
        self.assertTrue(self.m.is_suspended(code='000001.SZ', datestr=''))
        # 星期六
        self.assertTrue(self.m.is_suspended(code='000001.SZ',
                                            datestr='20191012'))
        self.assertFalse(self.m.is_suspended(code='000001.SZ',
                                             datestr='20191021'))

    def test_buy_check(self):
        code = "000001.SZ"
        # is_suspended
        ok, price = self.m.buy_check(code='', datestr='')
        self.assertFalse(ok)
        self.assertEqual(0, price)
        datestr = "20191021"
        # print(self.m.codes_history["000001.SZ"].loc[datestr])
        # [high, low] = [16.97, 16.43]
        # 买入竞价低于最低价，不能成交
        ok, price = self.m.buy_check(code=code, datestr=datestr,
                                     bid_price=11)
        self.assertFalse(ok)

        # 买入竞价在最低最高价之间， 可以成交
        ok, price = self.m.buy_check(code=code, datestr=datestr,
                                     bid_price=16.51)
        self.assertTrue(ok)
        self.assertEqual(16.51, price)

        # 买入竞价高于最高介， 可以成交
        ok, price = self.m.buy_check(code=code, datestr=datestr,
                                     bid_price=17)
        self.assertTrue(ok)
        self.assertEqual(16.97, price)

    def test_top_pct_change(self):
        # 涨跌停
        ts_token = os.getenv("TUSHARE_TOKEN")
        codes = ["600237.SH"]
        # self.indexs = []
        m = Market(
            ts_token=ts_token,
            start=self.start,
            end=self.end,
            codes=codes,
            indexs=self.indexs,
            data_dir=self.data_dir)
        code = "600237.SH"
        datestr = "20190701"
        ok, price = m.buy_check(code=code, datestr=datestr,
                                bid_price=4.5)
        self.assertFalse(ok)
        ok, price = m.sell_check(code=code, datestr=datestr,
                                 bid_price=4.5)
        self.assertTrue(ok)
        # 封涨停, 以涨停价成交
        self.assertEqual(4.55, price)

    def test_sell_check(self):
        code = "000001.SZ"
        # is_suspended
        ok, price = self.m.sell_check(code='', datestr='')
        self.assertFalse(ok)
        self.assertEqual(0, price)
        datestr = "20191021"
        # [high, low] = [16.97, 16.43]
        # 卖出入竞价高于最高价，不能成交
        ok, price = self.m.sell_check(code=code, datestr=datestr,
                                      bid_price=17)
        self.assertFalse(ok)

        # 买入竞价在最低最高价之间， 可以成交
        ok, price = self.m.sell_check(code=code, datestr=datestr,
                                      bid_price=16.51)
        self.assertTrue(ok)
        self.assertEqual(16.51, price)

        # 卖出竞价低于最低价， 可以成交, 按最低价成交
        ok, price = self.m.sell_check(code=code, datestr=datestr, bid_price=16)
        self.assertTrue(ok)
        self.assertEqual(16.43, price)


if __name__ == '__main__':
    unittest.main()
