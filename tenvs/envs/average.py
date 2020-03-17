# -*- coding:utf-8 -*-

import numpy as np

from tenvs.envs.base import BaseEnv
from tenvs.logger import logger


class AverageEnv(BaseEnv):
    """
    多支股票平均分仓日内买卖
    action: [scaled_sell_price, scaled_buy_price]*n, 取值[-1, 1], 对应[-0.1, 0.1]
    即: 出价较前一交易日的涨跌幅
    n: 是股票的个数
    对每支股票, 先以sell_price 卖出, 再以 buy_price 买进
    NOTE(wen): 实际交易时，可能与模拟环境存在差异
        1. 先到最高价，然后再到最低价：与模拟环境一致
        2. 先到最低价，再到最高价，这里出价有两种情况
            有现金，则按最低价买进，与模拟环境一致
            无现金(满仓)，模拟环境可以成交，实盘交易时的成交状态不一定可以成交
    """

    def __init__(self, market=None, investment=100000.0, look_back_days=10,
                 used_infos=["equities_hfq_info", "indexs_info"],
                 reward_fn="daily_return_add_price_bound", log_deals=False):
        """
        investment: 初始资金
        look_back_days: 向前取数据的天数
        """
        super(AverageEnv, self).__init__(market, investment, look_back_days,
                                         used_infos, reward_fn, log_deals)
        self.avg_percent = 1.0 / self.n
        self.action_space = 2 * self.n
        self.start = market.start
        self.portfolio_info_size = 2 * self.n
        self.input_size = self.market_info_size + self.portfolio_info_size

    def get_init_portfolio_obs(self):
        # 初始持仓 状态
        one_day = np.array([0] * (self.n * 2))
        obs = np.array([one_day] * self.look_back_days)
        return obs

    def get_init_obs(self):
        """
        obs 由两部分组成: 市场信息, 帐户信息(收益率, 持仓量)
        """
        market_info = []
        for date in self.dates[: self.look_back_days]:
            market_info.append(self.get_market_info(date))
        market_info = np.array(market_info)
        portfolio_info = self.get_init_portfolio_obs()
        return np.concatenate((market_info, portfolio_info), axis=1)

    def get_action_price(self, action, code):
        pre_close = self.market.get_pre_close_price(
            code, self.current_date)
        logger.debug("%s %s pre_close: %.2f" %
                     (self.current_date, code, pre_close))
        [v_sell, v_buy] = action
        # scale [-1, 1] to [-0.1, 0.1]
        pct_sell, pct_buy = v_sell * 0.1, v_buy * 0.1
        sell_price = round(pre_close * (1 + pct_sell), 2)
        buy_price = round(pre_close * (1 + pct_buy), 2)
        return sell_price, buy_price

    def do_action(self, action, pre_portfolio_value, only_update):
        cash_change = 0
        # 更新拆分信息
        for i in range(self.n):
            code = self.codes[i]
            divide_rate = self.market.get_divide_rate(code, self.current_date)
            self.portfolios[i].update_before_trade(divide_rate)
        sell_prices, buy_prices = [], []
        if only_update:
            sell_prices, buy_prices = [0] * self.n, [0] * self.n
        if not only_update:
            # 卖出
            for i in range(self.n):
                code = self.codes[i]
                act_i = action[2 * i: 2 * (i + 1)]
                sell_price, _ = self.get_action_price(act_i, code)
                sell_prices.append(sell_price)

                sell_cash_change, ok = self.sell(i, sell_price, 0)
                cash_change += sell_cash_change
            # 买进
            for i in range(self.n):
                code = self.codes[i]
                act_i = action[2 * i: 2 * (i + 1)]
                _, buy_price = self.get_action_price(act_i, code)
                buy_prices.append(buy_price)

                buy_cash_change, ok = self.buy(i, buy_price, self.avg_percent)
                cash_change += buy_cash_change

        logger.debug("do_action: time_id: %d, cash_change: %.1f" % (
            self.current_time_id, cash_change))

        # update
        for i in range(self.n):
            code = self.codes[i]
            close_price = self.market.get_close_price(code, self.current_date)
            self.portfolios[i].update_after_trade(
                close_price=close_price,
                cash_change=cash_change,
                pre_portfolio_value=pre_portfolio_value)
        return sell_prices, buy_prices

    def _next(self):
        market_info = self.get_market_info(self.current_date)
        portfolio_info = []
        for i in range(self.n):
            portfolio_info.append(self.portfolios[i].daily_return)
            portfolio_info.append(self.portfolios[i].value_percent)
        portfolio_info = np.array(portfolio_info)
        new_obs = np.concatenate((market_info, portfolio_info), axis=0)
        obs = np.concatenate((self.obs[1:, :],
                              np.array([new_obs])), axis=0)
        if not self.done:
            self.current_time_id += 1
            self.current_date = self.dates[self.current_time_id]
        self.pre_cash = self.cash
        return obs

    def get_buy_close_action(self, datestr):
        """
        在datestr以收盘价买进的action, 用于buy_and_hold策略,
        给出的action为: [0, v] * self.n, v为收盘价对应的action值
        """
        action = []
        for code in self.codes:
            pct = self.market.codes_history[code].loc[datestr,  "pct_chg"]
            buy_act_v = self.scale_pct_to_action_value(pct)
            # NOTE: 卖出价格默认为：昨日收盘价
            sell_act_v = 0
            action.append(sell_act_v)
            action.append(buy_act_v)
        return action
