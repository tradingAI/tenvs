# -*- coding:utf-8 -*-
import os

import pandas as pd
import tushare as ts

from tenvs.logger import logger


class Market:
    """
    模拟市场，加载环境所需要的数据
    NOTE(wen):
        从多数实验可以发现，使用后复权的数据做为模型输入，性能更优， Market统一使用
        后复权数据做模型的输入, 而不复权的数据做买卖的判断
    indexs:
        000001.SH: 上证指数
        399001.SZ: 深证成指
        ...
    NOTE(wen): 使用tushare下载指数日线信息需要在tushare.pro帐户中有200积分
    data_dir: 存储数据文件的目录，以降低重复下载的频率
    """

    def __init__(self,
                 ts_token="",
                 start="20190101",
                 end="20200101",
                 codes=["000001.SZ"],
                 indexs=["000001.SH", "399001.SZ"],
                 data_dir="/tmp/tenvs"):
        ts.set_token(ts_token)
        self.start = start
        self.end = end
        self.codes = codes
        self.indexs = indexs
        self.data_dir = data_dir
        self.load_codes_history()
        self.load_indexs_history()
        # hfq数据: 去除不复权数据(9列) 和复权因子(1列): 10, 从第11列开始是后复权数据
        self.equity_hfq_info_start_index = 10
        self.init_market_info()
        self.init_size_info()

    def get_info_size(self, info_name):
        date = self.open_dates[0]
        return len(self.market_info[date][info_name])

    def init_size_info(self):
        """
        初始化数据的size
        """
        self.equity_hfq_info_size = self.get_info_size("equities_hfq_info")
        self.indexs_info_size = self.get_info_size("indexs_info")

    def get_code_history(self, code, adj=None):
        return ts.pro_bar(
            ts_code=code, adj=adj,
            start_date=self.start, end_date=self.end)

    def load_codes_history(self):
        """
        self.codes_history: dict
        每条记录由两部分数据组成: 复权因子(1列), 不复权数据(9列), 后复权数据(9列)
            复权因子: adj_factor(1列)
            不复权OHLCV, ... (9列)
            后复权OHLCV, ... (9列)

        self.codes_history[code].columns的值为:
        [u'adj_factor', u'open', u'high', u'low', u'close', u'pre_close',
        u'change', u'pct_chg', u'vol', u'amount', u'open_hfq', u'high_hfq',
        u'low_hfq', u'close_hfq', u'pre_close_hfq', u'change_hfq',
        u'pct_chg_hfq', u'vol_hfq', u'amount_hfq']
        """

        self.codes_history = {}
        for code in self.codes:
            dir = os.path.join(self.data_dir, code)
            if not os.path.exists(dir):
                os.makedirs(dir)
            data_path = os.path.join(dir,
                                     self.start + "-" + self.end + ".csv")
            if os.path.exists(data_path):
                df = pd.read_csv(data_path)
                df = df.set_index("trade_date")
                df.index = df.index.astype(str, copy=False)
                self.codes_history[code] = df

            else:
                # 不复权
                df_bfq = self.get_code_history(code, adj=None)
                df_bfq = df_bfq.drop(columns=["ts_code"], axis=1)
                # 后复权
                df_hfq = self.get_code_history(code, adj="hfq")
                df_hfq = df_hfq.drop(columns=["ts_code"], axis=1)
                df = pd.merge(df_bfq, df_hfq,
                              on='trade_date', how='left',
                              suffixes=('', '_hfq'))
                # 拆分因子
                col_name = df.columns.tolist()
                col_name.insert(0, 'adj_factor')
                df = df.reindex(columns=col_name)
                df["adj_factor"] = df["close_hfq"] / df["close"]
                df = df.sort_values(by="trade_date", ascending=True)
                df = df.set_index("trade_date")
                df.index = df.index.astype(str, copy=False)
                df.to_csv(data_path)
                self.codes_history[code] = df

    def load_indexs_history(self):
        self.indexs_history = {}
        # 默认加载: 000001.SH(上证指数), 399001.SZ(深城证指)
        indexs = ["000001.SH", "399001.SZ"]
        for code in self.indexs:
            if code not in indexs:
                indexs.append(code)

        for code in indexs:
            dir = os.path.join(self.data_dir, "indexs", code)
            if not os.path.exists(dir):
                os.makedirs(dir)
            data_path = os.path.join(dir,
                                     self.start + "-" + self.end + ".csv")
            if os.path.exists(data_path):
                df = pd.read_csv(data_path)
                df = df.set_index("trade_date")
                df.index = df.index.astype(str, copy=False)
                self.indexs_history[code] = df
            else:
                pro = ts.pro_api()
                df = pro.index_daily(ts_code=code,
                                     start_date=self.start,
                                     end_date=self.end)
                df = df.drop(columns=["ts_code"], axis=1)
                df = df.sort_values(by="trade_date", ascending=True)
                df = df.set_index("trade_date")
                df.index = df.index.astype(str, copy=False)
                df.to_csv(data_path)
                self.indexs_history[code] = df

    def set_pre_info(self):
        date = self.open_dates[0]
        self.equities_pre_hfq_info = {}
        self.equities_pre_bfq_info = {}
        for code in self.codes:
            # 如果第一天就停牌，这里会出错，建议另外选择一天开始回测
            try:
                data = self.codes_history[code].loc[date].tolist()
                bfq_data = data[1: self.equity_hfq_info_start_index]
                # 开盘时， open=1
                bfq_data.append(1)
                self.equities_pre_bfq_info[code] = bfq_data
                # 后复权
                hfq_data = data[self.equity_hfq_info_start_index:]
                # 开盘时， open=1
                hfq_data.append(1)
                self.equities_pre_hfq_info[code] = hfq_data
            except Exception as e:
                print("%s, %s停牌，建议另外选择一天开始回测" % (code, date))
                print(e)
                exit()

    def get_equities_bfq_info(self, date):
        info = []
        for code in self.codes:
            data = None
            if date in self.codes_history[code].index:
                data = self.codes_history[code].loc[date].tolist()
                data = data[1: self.equity_hfq_info_start_index]
                # 开盘时， open=1
                data.append(1)
            else:
                # 如果停牌则使用前一开盘日信息
                data = self.equities_pre_bfq_info[code]
                data[-1] = 0
            # 更新前一开盘日信息
            self.equities_pre_bfq_info[code] = data
            info.extend(data)
        return info

    def get_equities_hfq_info(self, date):
        info = []
        for code in self.codes:
            data = None
            if date in self.codes_history[code].index:
                data = self.codes_history[code].loc[date].tolist()
                data = data[self.equity_hfq_info_start_index:]
                # 开盘时， open=1
                data.append(1)
            else:
                # 如果停牌则使用前一开盘日信息
                data = self.equities_pre_hfq_info[code]
                data[-1] = 0
            # 更新前一开盘日信息
            self.equities_pre_hfq_info[code] = data
            info.extend(data)
        return info

    def get_indexs_info(self, date):
        info = []
        for code in self.indexs:
            data = self.indexs_history[code].loc[date].tolist()
            info.extend(data)
        return info

    def init_market_info(self):
        """
        以日期为key, 将市场相关信息组织在一个dict中:
            equities_hfq_info: 合并之后的个股信息, 如果某支股停牌，则使用它前一开盘日信息
            indexs_info: 合并之后指数信息
        Note(wen): 添加其他市场相关信息，都放在这里
        """
        self.open_dates = self.indexs_history["000001.SH"].index.tolist()
        self.open_dates.sort()
        self.set_pre_info()
        self.market_info = {}
        for date in self.open_dates:
            self.market_info[date] = {}
            self.market_info[date]["equities_bfq_info"] = \
                self.get_equities_bfq_info(date)
            self.market_info[date]["equities_hfq_info"] = \
                self.get_equities_hfq_info(date)
            self.market_info[date]["indexs_info"] = self.get_indexs_info(date)

    def is_suspended(self, code='', datestr=''):
        # 是否停牌，是：返回 True, 否：返回 False
        if code not in self.codes_history:
            return True
        if datestr not in self.codes_history[code].index:
            return True
        return False

    def buy_check(self, code='', datestr='', bid_price=None):
        # 返回：OK, 成交价
        ok = False
        # 停牌
        if self.is_suspended(code, datestr):
            return ok, 0
        # 获取当天标的信息
        [open, high, low, pct_change] = self.codes_history[code].loc[
            datestr, ["open", "high", "low", "pct_chg"]]
        # 涨停封板, 无法买入
        if low == high and pct_change > self.top_pct_change:
            logger.debug(u"sell_check %s %s 涨停法买进" % (code, datestr))
            return ok, 0
        # 买入竞价低于最低价，不能成交
        if bid_price < low:
            return ok, 0
        # 买入竞价高于最低价， 可以成交
        if bid_price >= low:
            return True, min(bid_price, high)

    def sell_check(self, code='', datestr='', bid_price=None):
        # 返回：OK, 成交价
        ok = False
        # 停牌
        if self.is_suspended(code, datestr):
            return ok, 0
        # 获取当天标的信息
        [open, high, low, pct_change] = self.codes_history[code].loc[
            datestr, ["open", "high", "low", "pct_chg"]]
        # 跌停封板， 不能卖出
        if low == high and pct_change < -self.top_pct_change:
            logger.debug(u"sell_check %s %s 跌停无法卖出" % (code, datestr))
            return ok, 0
        # 卖出竞价高于最高价，不可以成交
        if bid_price > high:
            return ok, 0
        # 卖出竞价在最低最高价之间， 可以成交，按出价成交
        # NOTE: 这里卖出竞价低于最低价时，可以成交，按最低价成交
        if bid_price <= high:
            ok = True
            return ok, max(bid_price, low)

    def get_pre_close_price(self, code, datestr):
        if datestr in self.codes_history[code].index:
            return self.codes_history[code].loc[datestr]["pre_close"]
        # 如果当天停牌, 返回前一开市日的pre_close
        df = self.codes_history[code]
        df_ = df[df.index < datestr]
        return df_.iloc[-1]["pre_close"]

    def get_close_price(self, code, datestr):
        if datestr in self.codes_history[code].index:
            return self.codes_history[code].loc[datestr]["close"]
        # 如果当天停牌, 返回前一开市日收盘价
        df = self.codes_history[code]
        df_ = df[df.index < datestr]
        return df_.iloc[-1]["close"]

    def get_pre_adj_factor(self, code, datestr):
        df = self.codes_history[code]
        df_ = df[df.index < datestr]
        return df_.iloc[-1]["adj_factor"]

    def get_adj_factor(self, code, datestr):
        if self.is_suspended(code=code, datestr=datestr):
            return self.get_pre_adj_factor(code, datestr)
        else:
            return self.codes_history[code].loc[datestr]["adj_factor"]

    def get_divide_rate(self, code, datestr):
        pre_adj_factor = self.get_pre_adj_factor(code, datestr)
        current_adj_factor = self.get_adj_factor(code, datestr)
        return current_adj_factor / pre_adj_factor
