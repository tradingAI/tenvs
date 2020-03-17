# -*- coding:utf-8 -*-
import random
import time

import gym
import numpy as np

from tenvs.envs.reward import get_reward_func
from tenvs.logger import logger
from tenvs.portfolio import Portfolio


class BaseEnv(gym.Env):
    def __init__(self, market=None, investment=100000.0, look_back_days=10,
                 used_infos=["equities_hfq_info", "indexs_info"],
                 reward_fn="daily_return_add_price_bound", log_deals=False):
        """
        investment: 初始资金
        look_back_days: 向前取数据的天数
        """
        self.market = market
        # 股票数量
        self.n = len(market.codes)
        self.codes = market.codes
        self.start = market.start
        self.end = market.end
        self.look_back_days = look_back_days
        self.investment = investment
        # 输入数据: 个股信息 + 指数信息
        self.used_infos = used_infos
        self.market_info_size = self.get_market_info_size()
        # 开市日期列表
        self.dates = market.open_dates
        # 记录一个回合的收益序列
        self.returns = []
        self.reward_fn = get_reward_func(name=reward_fn)
        self.reward_fn_name = reward_fn
        self.log_deals = log_deals

    def get_market_info_size(self):
        size = 0
        for info_name in self.used_infos:
            size += self.market.get_info_size(info_name)
        return size

    def _init_current_time_id(self):
        return self.look_back_days

    def get_market_info(self, date):
        info = []
        for info_name in self.used_infos:
            data = self.market.market_info[date][info_name]
            info.extend(data)
        return np.array(info)

    def get_hlc_prices(self):
        date = self.current_date
        highs, lows, closes = [], [], []
        for i in range(self.n):
            code = self.codes[i]
            if date in self.market.codes_history[code].index:
                highs.append(self.market.codes_history[code].loc[date, "high"])
                lows.append(self.market.codes_history[code].loc[date, "low"])
                closes.append(self.market.codes_history[code].loc[date,
                                                                  "close"])
            else:
                # 停牌时
                highs.append(0)
                lows.append(0)
                closes.append(0)
        return highs, lows, closes

    def update_reward(self, sell_prices, buy_prices):
        if self.reward_fn_name in ["daily_return", "simple"]:
            self.reward = self.reward_fn(self.daily_return)
        else:
            highs, lows, closes = self.get_hlc_prices()
            self.reward = self.reward_fn(
                self.daily_return, highs, lows, closes,
                sell_prices, buy_prices)
        # 每一只股的reward与总的reward一致
        for i in range(self.n):
            self.rewards[i] = self.reward

    def sell(self, id, price, target_pct):
        # id: code id
        code = self.codes[id]
        logger.debug("sell %s, bid price: %.2f" % (code, price))
        ok, price = self.market.sell_check(
            code=code,
            datestr=self.current_date,
            bid_price=price)
        if ok:
            # 全仓卖出
            cash_change, price, vol = self.portfolios[
                id].order_target_percent(
                    percent=target_pct, price=price,
                    pre_portfolio_value=self.portfolio_value,
                    current_cash=self.cash)
            self.cash += cash_change
            if vol != 0:
                self.info["orders"].append(["sell", code,
                                            round(cash_change, 1),
                                            round(price, 2), vol])
            logger.debug("sell %s target_percent: 0, cash_change: %.3f" %
                         (code, cash_change))
            return cash_change, ok
        return 0, ok

    def buy(self, id, price, target_pct):
        # id: code id
        code = self.codes[id]
        logger.debug("buy %s, bid_price: %.2f" % (code, price))
        ok, price = self.market.buy_check(
            code=code,
            datestr=self.current_date,
            bid_price=price)
        pre_cash = self.cash
        if ok:
            # 分仓买进
            cash_change, price, vol = self.portfolios[id].order_target_percent(
                percent=target_pct, price=price,
                pre_portfolio_value=self.portfolio_value,
                current_cash=self.cash)
            self.cash += cash_change
            if vol != 0:
                self.info["orders"].append(["buy", code,
                                            round(cash_change, 1),
                                            round(price, 2), vol])
            logger.debug("buy %s cash: %.1f, cash_change: %1.f" %
                         (code, pre_cash, cash_change))
            return cash_change, ok
        return 0, ok

    def update_portfolio(self):
        pre_portfolio_value = self.portfolio_value
        self.market_value = 0
        self.daily_pnl = 0
        self.pnl = 0
        self.transaction_cost = 0
        self.all_transaction_cost = 0
        for p in self.portfolios:
            self.market_value += p.market_value
            self.daily_pnl += p.daily_pnl
            self.pnl += p.pnl
            self.transaction_cost += p.transaction_cost
            self.all_transaction_cost += p.all_transaction_cost
        self.total_pnl += self.pnl

        # 当日收益率 更新
        if pre_portfolio_value == 0:
            self.daily_return = 0
        else:
            self.daily_return = self.daily_pnl / pre_portfolio_value
        # update portfolio_value
        self.portfolio_value = self.market_value + self.cash
        self.portfolio_value_logs.append(self.portfolio_value)

    def update_value_percent(self):
        if self.portfolio_value == 0:
            self.value_percent = 0.0
        else:
            self.value_percent = self.market_value / self.portfolio_value
        for i in range(self.n):
            self.portfolios[i].update_value_percent(self.portfolio_value)

    def get_init_obs():
        raise NotImplementedError

    def reset(self):
        # 当前时间
        self.current_time_id = self._init_current_time_id()
        self.current_date = self.dates[self.current_time_id]
        self.done = False
        # 当日的回报
        self.reward = 0
        self.rewards = [0] * self.n
        # 累计回报
        self.total_reward = 0.0
        # 当日订单集合
        self.info = {"orders": []}
        # 总权益
        self.portfolio_value = self.investment
        # 初始资金
        self.starting_cash = self.investment
        # 可用资金
        self.cash = self.investment
        self.pre_cash = self.cash
        self.total_pnl = 0

        # 每只股的 portfolio
        self.portfolios = []
        for code in self.codes:
            self.portfolios.append(Portfolio(code=code,
                                             log_deals=self.log_deals))
        self.obs = self.get_init_obs()
        self.portfolio_value_logs = []
        return self.obs

    def step(self, action, only_update=False):
        """
        only_update为True时，表示buy_and_hold策略，可作为一种baseline策略
        """
        self.action = action
        self.info = {"orders": []}
        if self.log_deals:
            logger.info("=" * 50 + "%s" % self.current_date + "=" * 50)
        logger.debug("=" * 50 + "%s" % self.current_date + "=" * 50)
        logger.debug("current_time_id: %d, portfolio: %.1f" %
                     (self.current_time_id, self.portfolio_value))
        logger.debug("step action: %s" % str(action))

        # 到最后一天
        if self.current_date == self.dates[-1]:
            self.done = True

        pre_portfolio_value = self.portfolio_value
        sell_prices, buy_prices = self.do_action(action,
                                                 pre_portfolio_value,
                                                 only_update)
        self.update_portfolio()
        self.update_value_percent()
        self.update_reward(sell_prices, buy_prices)
        self.obs = self._next()
        self.info = {
            "orders": self.info["orders"],
            "current_date": self.current_date,
            "portfolio_value": round(self.portfolio_value / self.investment, 3),
            "daily_pnl": round(self.daily_pnl, 1),
            "reward": self.reward}
        return self.obs, self.reward, self.done, self.info, self.rewards

    def get_random_action(self):
        return [random.uniform(-1, 1) for i in range(self.action_space)]

    def scale_pct_to_action_value(self, pct):
        """
        将pct值scale到action值上, pct取值: [-10.0, 10.0], action的取值: [-1, 1]
        """
        return pct * 0.1
