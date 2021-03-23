import copy

import numpy as np
from tenvs.accounts.const import (MIN_COMMISSION, NULL_CODE, NULL_PRICE,
                                  STK_BUY_COMMISSION_RATE,
                                  STK_SELL_COMMISSION_RATE)


class STKAccount:
    '''
    (默认)next_bar_open_price: 下一个Bar开盘价撮合
    current_bar_close_price: 当前Bar收盘价撮合
    high_low_price: 当前Bar最高最低价撮合
    vwap: 平均交易价格撮合
    '''

    def __init__(self, investment=1e5, codes=['000001.SZ']):
        # 当前持仓股票
        self.codes = codes
        # 空仓, 也认为是一只股票
        self.codes.append(NULL_CODE)
        # 跟踪股票数
        self.n = len(codes) + 1
        self.investment = investment
        # 当前总资产
        self.total_assets = investment
        # 前一bar的总资产
        self.pre_total_assets = investment
        # 资金余额
        self.balance = investment
        # 可用金额, NOTE(liuwen):可用金额与资金余额并不一定相等(有未成交买进时)
        self.available = investment
        # 股票市值(Market Capitalization), 简称Market Cap
        self.caps = np.zeros((self.n), np.float)
        self.caps[-1] = investment
        # 前一市值
        self.pre_caps = copy.deepcopy(self.caps)
        # 持仓量
        self.volumes = np.zeros((self.n), np.float)
        self.volumes[-1] = investment
        # 前一bar持仓量
        self.pre_volumes = np.zeros((self.n), np.float)
        self.pre_volumes[-1] = investment
        # 冻结量
        self.frozen_volumes = np.zeros((self.n), np.float)
        # 该仓位可卖出股数。T＋1 的市场中sellable = 所有持仓 - 已冻结
        self.sellable_volumes = np.zeros((self.n), np.float)
        # 当前价格
        self.prices = np.zeros((self.n), np.float)
        self.prices[-1] = NULL_PRICE
        # 前一价格
        self.pre_closes = np.zeros((self.n), np.float)
        self.pre_closes[-1] = NULL_PRICE
        # 获得该持仓的市场价值在股票账户中所占比例，取值范围[0, 1], 以总账户为基线
        self.weights = np.zeros((self.n), np.float)
        self.weights[-1] = 1.0
        # 当日盈亏
        self.daily_pnl = 0.0
        # 当日盈亏
        self.daily_pnls = np.zeros((self.n), np.float)
        # 累计盈亏, Profit and Loss(绝对金额)
        self.pnl = 0.0
        # 累计盈亏
        self.pnls = np.zeros((self.n), np.float)
        # 当前最新一天的日收益率, 以总账户为基线
        self.daily_return = 0.0
        self.daily_returns = np.zeros((self.n), np.float)

        # 累计收益率
        self.return_rate = 0.0
        self.return_rates = np.zeros((self.n), np.float)
        # 当日交易费
        self.daily_fee = 0.0
        self.daily_fees = np.zeros((self.n), np.float)
        # 累计交易费
        self.total_fee = 0.0

    def update_prices(self, prices):
        """
        由于市场价格变化，更新相关值
        NOTE(liuwen): prices[-1] == NULL_PRICE
        """
        assert prices[-1] == NULL_PRICE
        self.pre_closes = copy.deepcopy(self.prices)
        self.pre_caps = copy.deepcopy(self.caps)
        self.prices = prices
        self.caps = self.volumes * self.prices
        self.total_assets = np.sum(self.caps)

    def update_fees(self, cash_changes):
        self.daily_fees = [0] * self.n
        # NOTE(liuwen): NULL_CODE不需要缴费
        for i in range(self.n - 1):
            # 卖出
            if cash_changes[i] > 0:
                self.daily_fees[i] = max(
                    cash_changes[i] * STK_SELL_COMMISSION_RATE, MIN_COMMISSION)
            # 买进
            elif cash_changes[i] < 0:
                self.daily_fees[i] = max(
                    cash_changes[i] * STK_BUY_COMMISSION_RATE, MIN_COMMISSION)
        self.daily_fee = np.sum(self.daily_fees)
        self.total_fee += self.daily_fee

    def before_trade(self, adjusts: np.array, status=np.array, bars=np.array):
        '''
        bars.shape = (self.n, 5), 5=4(ohlc) + 1(vwap)
        '''
        pass

    def check_buy_orders(self, volumes: np.array, prices: np.array):
        # is_buys: True->买进, False-> 卖出/不交易
        is_buys = volumes > 0
        expected_buy_cash = volumes[is_buys] * prices[is_buys]
        assert self.available > np.sum(expected_buy_cash) * \
            (STK_BUY_COMMISSION_RATE + 1)

    def check_sell_orders(self, volumes: np.array, prices: np.array):
        # is_sells: True-> 卖出, False-> 买进/不交易
        is_sells = volumes < 0
        check_list = volumes[is_sells] <= self.sellable_volumes
        assert np.all(check_list)

    def check_null_code_volume(self, volumes: np.array):
        assert volumes[-1] + self.available > 0

    def trade(self, volumes: np.array, prices: np.array) -> np.array:
        '''
        volumes.shape: (self.n,), 包含了NULL_CODE
        prices.shape: (self.n,), 包含了NULL_CODE
        (默认)保守交易:
            1. 先根据self.available 决定买入量
            2. 再根据self.sellable_volumes 决定卖出量
        乐观交易:
            1. 先根据self.sellable_volumes 进行卖出，以获得更多的cash
            2. 再根据self.available 决定买入量
        '''
        self.check_buy_orders(volumes[:-1], prices[:-1])
        self.check_sell_orders(volumes[:-1], prices[:-1])
        self.check_null_code_volume(volumes)
        # volume > 0: 买进, cash_changes < 0
        # volume < 0: 卖出, cash_changes > 0
        cash_changes = -volumes * prices
        self.update_fees(cash_changes)
        cash_changes = cash_changes - self.daily_fees
        # 金额变化量
        self.available += np.sum(cash_changes[:-1])
        self.volumes += volumes
        self.volumes[-1] = self.available
        self.update_prices(prices)

    def after_trade(self, bars: np.array):
        pass
