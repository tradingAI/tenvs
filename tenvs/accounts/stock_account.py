import copy

import numpy as np
from tenvs.accounts.const import (MIN_COMMISSION, MONEY, MONEY_PRICE,
                                  STK_BUY_COMMISSION_RATE,
                                  STK_SELL_COMMISSION_RATE)
from tenvs.common.logger import logger


class StockAccount:
    '''
    NOTE(liuwen):
        每个bar只能提交一个订单:
            len(volumes) = len(codes) + 1
            volumes[i] > 0: 表示买入volumes[i]
            volumes[i] < 0: 表示卖出volumes[i]
            需要调用方约束: 可用余额，可卖股票量限制, 以降低实际交易时的撤单率
    (默认)bar_open_price: Bar开盘价撮合
    TODO(liuwen):
        bar_high_low_price: 当前Bar最高最低价撮合(Limit Price order)
        bar_vwap: 平均交易价格撮合(适合有算法交易执行情况下)
        bar_twap: 时间平均交易价格撮合(适合有算法交易执行情况下)
        bar_close_price: 当前Bar收盘价撮合
    TODO(liuwen): 验证逻辑正确性之后去除 assert
    '''

    def __init__(self, investment=1e5, codes=['000001.SZ']):
        # 当前持仓股票
        self.codes = codes
        # 空仓, 也认为是一只股票
        self.codes.append(MONEY)
        # 跟踪股票数
        self.n = len(codes)
        logger.info(f'codes: {codes}, {self.n}')
        self.investment = investment
        # 当前总资产
        self.total_assets = investment
        # 前一天总资产
        self.pre_day_total_assets = investment
        # 资金余额
        self.balance = investment
        # 可用金额, 有未成交买进时与资金余额不相等
        self.available = investment
        # 股票市值(Market Capitalization), 简称Market Cap
        self.caps = np.zeros((self.n), float)
        self.caps[-1] = investment
        # 资金变化
        self.bar_cash_changes = np.zeros((self.n), float)
        # 持仓量
        self.volumes = np.zeros((self.n), float)
        self.volumes[-1] = investment
        # 冻结量
        self.frozen_volumes = np.zeros((self.n), float)
        # 该仓位可卖出股数。T＋1 的市场中sellable = 所有持仓 - 已冻结
        self.sellable_volumes = np.zeros((self.n), float)
        # 当前价格
        self.prices = np.zeros((self.n), float)
        self.prices[-1] = MONEY_PRICE
        # 获得该持仓的市场价值在股票账户中所占比例，取值范围[0, 1], 以总账户为基线
        self.weights = np.zeros((self.n), float)
        self.weights[-1] = 1.0
        self.bar_pnl = 0.0
        self.bar_pnls = np.zeros((self.n), float)
        # 当日盈亏
        self.day_pnl = 0.0
        # 当日盈亏
        self.day_pnls = np.zeros((self.n), float)
        # 累计盈亏, Profit and Loss(绝对金额)
        self.pnl = 0.0
        # 累计盈亏
        self.pnls = np.zeros((self.n), float)
        # 当前最新一天的日收益率, 以总账户为基线
        self.day_return = 0.0
        self.day_returns = np.zeros((self.n), float)
        # 净值
        self.value = 1.0
        self.contributions = np.zeros((self.n), float)
        self.weights = np.zeros((self.n), float)
        self.weights[-1] = 1.0
        # 当日交易费
        self.day_fee = 0.0
        self.day_fees = np.zeros((self.n), float)
        self.day_cash_changes = np.zeros((self.n), float)
        # 累计交易费
        self.fee = 0.0

    def day_init(self, pre_day_closes: np.array):
        '''
        每天交易前需要调用
        pre_closes.shape = (self.n,)
        '''
        assert pre_day_closes[-1] == MONEY_PRICE
        self.pre_day_total_assets = self.total_assets
        # 如果有拆分股票，则按市值不变进行调整
        self.volumes = self.caps / pre_day_closes
        # 当日盈亏
        self.day_pnl = 0.0
        self.day_pnls = np.zeros((self.n), float)
        # 当前最新一天的日收益率, 以总账户为基线
        self.day_return = 0.0
        self.day_returns = np.zeros((self.n), float)
        # 可用资金
        self.available = self.balance
        # 可卖
        self.sellable_volumes = copy.deepcopy(self.volumes)
        # 冻结量
        self.frozen_volumes = np.zeros((self.n), float)
        # 当天交易变化金额
        self.day_cash_changes = np.zeros((self.n), float)
        # 当日交易费
        self.day_fees = np.zeros((self.n), float)
        self.day_fee = 0.0
        self.bar_cash_changes = 0.0

    def update_fees(self, cash_changes):
        # TODO(liuwen): 优化计算逻辑(if-else => vector op)
        fees = [0] * self.n
        # NOTE(liuwen): MONEY不需要缴费
        for i in range(self.n - 1):
            # 卖出
            if cash_changes[i] > 0:
                fees[i] = max(
                    cash_changes[i] * STK_SELL_COMMISSION_RATE, MIN_COMMISSION)
            # 买进
            elif cash_changes[i] < 0:
                fees[i] = max(
                    cash_changes[i] * STK_BUY_COMMISSION_RATE, MIN_COMMISSION)
        fees = np.around(fees, 6)
        self.day_fees += fees
        self.day_fee = np.sum(self.day_fees)
        self.fee += self.day_fee

    def check_buy_orders(self, volumes: np.array, prices: np.array):
        # fill sell orders by 0
        filled_volumes = np.maximum(volumes, np.zeros((self.n-1), float))
        # 不包含最后一项(MONEY项)
        expected_buy_cash = np.sum((filled_volumes * prices))
        assert self.available > np.sum(expected_buy_cash) * \
            (STK_BUY_COMMISSION_RATE + 1)

    def check_sell_orders(self, volumes: np.array):
        assert np.all((volumes[:-1] + self.sellable_volumes[:-1]) >= 0)

    def check_money_volume(self, volumes: np.array):
        assert volumes[-1] + self.available > 0

    def bar_settlement(self, closes):
        """
        bar结束时，根据bar.closes进行结算, 计算pnls
        NOTE(liuwen): prices[-1] == MONEY_PRICE
        """
        assert closes[-1] == MONEY_PRICE
        self.prices = closes
        pre_bar_caps = copy.deepcopy(self.caps)
        self.caps = np.around(self.volumes * self.prices, 6)
        pre_bar_total_assets = self.total_assets
        assert pre_bar_total_assets > 0
        self.total_assets = np.sum(self.caps)
        # pnl
        self.bar_pnl = self.total_assets - pre_bar_total_assets
        self.bar_pnl = np.around(self.bar_pnl, 6)
        self.bar_pnls = self.caps + self.bar_cash_changes - pre_bar_caps
        self.bar_pnls = np.around(self.bar_pnls, 6)
        # MONEY pnl为0
        self.bar_pnls[-1] = 0
        assert np.around(self.bar_pnl, 6) == np.around(
            np.sum(self.bar_pnls), 6)
        self.day_pnl += self.bar_pnl
        self.day_pnls += self.bar_pnls
        self.pnl += self.bar_pnl
        self.pnls += self.bar_pnls
        # return rate
        self.day_return = self.day_pnl / self.pre_day_total_assets
        self.day_returns = self.day_pnls / self.pre_day_total_assets
        self.value = np.around(self.pnl / self.investment + 1.0, 8)
        self.contributions = np.around(self.pnls / self.investment, 8)
        # 权重
        self.weights = self.caps / self.total_assets

    def bar_log(self, day, id):
        logger.info(
            f'day={day}, bar={id}, bar_pnl={self.bar_pnl: .2f}')

    def day_log(self, day):
        logger.info(f'day={day}, day_pnl={self.day_pnl: .2f}')
        logger.info(f'day={day}, available={self.available: .2f}')

    def bar_execute(self, volumes: np.array, bar: dict,
                    bar_id=0, day_log=False, day='20210101') -> np.array:
        '''
        volumes.shape: (self.n,), 包含了MONEY
        bar:
            pre_bar_closes.shape: (self.n,), 包含了MONEY
            opens.shape: (self.n,)
            pre_day_close.shape: (self.n)
            closes.shape: (self.n,)
            highs.shape: (self.n,) # 可选
            lows.shape: (self.n,) # 可选
            vwap.shape: (self.n,) # 可选

        (默认)保守交易:
            1. 先根据self.available 决定买入量
            2. 再根据self.sellable_volumes 决定卖出量
        乐观交易:
            1. 先根据self.sellable_volumes 进行卖出，以获得更多的cash
            2. 再根据self.available 决定买入量
        '''
        volumes = volumes.astype(float)
        assert len(volumes) == self.n
        if bar_id == 0:
            self.day_init(bar['pre_day_close'])
        prices = bar['opens']
        self.check_money_volume(volumes)
        self.check_buy_orders(volumes[:-1], prices[:-1])
        self.check_sell_orders(volumes)

        # volume > 0: 买进, cash_changes < 0
        # volume < 0: 卖出, cash_changes > 0
        self.bar_cash_changes = -volumes * prices
        self.update_fees(self.bar_cash_changes)
        self.bar_cash_changes -= self.day_fees

        # 金额变化量
        total_cash_change = np.around(np.sum(self.bar_cash_changes[:-1]), 6)
        # MONEY
        self.bar_cash_changes[-1] = total_cash_change
        self.day_cash_changes += self.bar_cash_changes
        self.balance = np.around(self.balance + total_cash_change, 6)
        self.available = np.around(self.available + total_cash_change, 6)
        volumes[-1] = total_cash_change
        self.volumes = np.around(self.volumes + volumes, 6)
        # 可卖， 减去卖出的部分
        self.sellable_volumes += np.minimum(volumes,
                                            np.zeros((self.n), float))
        self.sellable_volumes = np.around(self.sellable_volumes, 6)
        # 冻结, 加上买进的部分
        self.frozen_volumes += np.maximum(volumes,
                                          np.zeros((self.n), float))
        logger.info(self.volumes[-1])
        logger.info(self.available)
        assert self.volumes[-1] == self.available
        self.bar_settlement(bar['closes'])
        self.bar_log(day, bar_id)
        if day_log:
            self.day_log(day)
