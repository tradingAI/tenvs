# -*- coding:utf-8 -*-

import logging
import unittest

from portfolio import Portfolio

logging.root.setLevel(logging.ERROR)


class TestPortfolio(unittest.TestCase):

    def test_update_value_percent(self):
        p = Portfolio()
        p.update_value_percent(0)
        self.assertEqual(0, p.value_percent)
        p.market_value = 10
        p.update_value_percent(100.0)
        self.assertEqual(0.1, p.value_percent)

    def test_fee(self):
        p = Portfolio()
        self.assertEqual(5.0, p._buy_fee(0))
        self.assertEqual(5.0, p._buy_fee(1000))
        self.assertEqual(10.0, p._buy_fee(10000))
        self.assertEqual(0, p._sell_fee(0))
        self.assertEqual(1.5, p._sell_fee(1000))

    def test_buy(self):
        p = Portfolio(
            buy_commission_rate=0.001,
            sell_commission_rate=0.0015,
            min_commission=5.0, round_lot=100)
        self.assertEqual((-10010.0, 10.0, 1000),
                         p.buy(price=10.0, volume=1000))
        self.assertEqual(10.0, p.transaction_cost)
        self.assertEqual(10.01, p.avg_price)
        self.assertEqual(10.0, p._price)
        self.assertEqual(1000, p.volume)
        self.assertEqual(1000, p.frozen_volume)
        self.assertEqual(10.0, p.all_transaction_cost)
        self.assertEqual((-10010.0, 10.0, 1000),
                         p.buy(price=10.0, volume=1000))
        self.assertEqual(20.0, p.transaction_cost)
        self.assertEqual(10.01, p.avg_price)
        self.assertEqual(10.0, p._price)
        self.assertEqual(2000, p.volume)
        self.assertEqual(2000, p.frozen_volume)
        self.assertEqual(20.0, p.all_transaction_cost)

    def test_update_befor_trade(self):
        p = Portfolio(
            buy_commission_rate=0.001,
            sell_commission_rate=0.0015,
            min_commission=5.0, round_lot=100)
        p.buy(price=10.0, volume=1000)
        p.update_before_trade(divide_rate=1.0)
        self.assertEqual(1000, p.sellable)
        self.assertEqual(0, p.frozen_volume)
        self.assertEqual(0, p.transaction_cost)

        p = Portfolio(
            buy_commission_rate=0.001,
            sell_commission_rate=0.0015, min_commission=5.0, round_lot=100,
            divide_rate_threshold=1.005)
        p.buy(price=10.0, volume=1000)
        p.update_before_trade(divide_rate=1.1)
        self.assertEqual(1100, p.volume)
        self.assertEqual(1100, p.sellable)
        # 有拆分
        p.update_before_trade(divide_rate=1.006)
        self.assertEqual(1106, p.volume)
        self.assertEqual(1106, p.sellable)
        # 没有拆分
        p.update_before_trade(divide_rate=1.005)
        self.assertEqual(1106, p.volume)
        self.assertEqual(1106, p.sellable)

    def test_sell(self):
        p = Portfolio(
            buy_commission_rate=0.001,
            sell_commission_rate=0.0015, min_commission=5.0, round_lot=100)
        self.assertEqual((-10010.0, 10.0, 1000),
                         p.buy(price=10.0, volume=1000))
        p.update_before_trade(divide_rate=1.0)
        p.sell(price=11, volume=500)
        self.assertEqual(8.25, p.transaction_cost)
        self.assertEqual(9.0365, p.avg_price)
        self.assertEqual(11.0, p._price)
        self.assertEqual(500, p.volume)
        self.assertEqual(500, p.sellable)
        self.assertEqual(18.25, p.all_transaction_cost)
        p.sell(price=11, volume=500)
        self.assertEqual(16.5, p.transaction_cost)
        self.assertEqual(0, p.avg_price)
        self.assertEqual(11, p._price)
        self.assertEqual(0, p.volume)
        self.assertEqual(0, p.sellable)
        self.assertEqual(26.5, p.all_transaction_cost)

    def test_submit_order(self):
        p = Portfolio(
            buy_commission_rate=0.001,
            sell_commission_rate=0.0015, min_commission=5.0, round_lot=100)
        self.assertEqual((-10010.0, 10.0, 1000),
                         p._submit_order(side="buy", price=10.0, volume=1000))
        p.update_before_trade(divide_rate=1.0)
        self.assertEqual((5491.75, 11, 500),
                         p._submit_order(side="sell", price=11, volume=500))
        self.assertEqual(8.25, p.transaction_cost)
        self.assertEqual(9.0365, p.avg_price)
        self.assertEqual(500, p.volume)
        self.assertEqual(18.25, p.all_transaction_cost)

    def test_sell_all_stock(self):
        p = Portfolio(
            buy_commission_rate=0.001,
            sell_commission_rate=0.0015, min_commission=5.0, round_lot=100)
        # sellable==0 , 无可卖
        self.assertEqual((0.0, 10, 0), p._sell_all_stock(price=10))
        self.assertEqual((-10010.0, 10.0, 1000),
                         p._submit_order(side="buy", price=10.0, volume=1000))
        p.update_before_trade(divide_rate=1.0)
        self.assertEqual((10983.5, 11, 1000), p._sell_all_stock(price=11))
        self.assertEqual(16.5, p.transaction_cost)
        self.assertEqual(0, p.avg_price)
        self.assertEqual(0, p.volume)
        self.assertEqual(26.5, p.all_transaction_cost)

    def test_order_value(self):
        p = Portfolio(
            buy_commission_rate=0.001,
            sell_commission_rate=0.0015, min_commission=5.0, round_lot=100)
        # buy
        self.assertEqual((-10010.0, 10, 1000),
                         p.order_value(amount=10000, price=10,
                                       current_cash=30000))
        self.assertEqual(10.0, p.transaction_cost)
        self.assertEqual(10.01, p.avg_price)
        self.assertEqual(1000, p.volume)
        self.assertEqual(1000, p.frozen_volume)
        self.assertEqual(10.0, p.all_transaction_cost)
        p.update_before_trade(divide_rate=1.0)
        # buy 超过 cash
        self.assertEqual((-19019.0, 10, 1900),
                         p.order_value(amount=20000, price=10,
                                       current_cash=19990))
        self.assertEqual(19.0, p.transaction_cost)
        self.assertEqual(10.01, p.avg_price)
        self.assertEqual(2900, p.volume)
        self.assertEqual(1900, p.frozen_volume)
        self.assertEqual(29.0, p.all_transaction_cost)
        # sell
        self.assertEqual((4992.5, 10, 500),
                         p.order_value(amount=-5000,
                         price=10, current_cash=971.0))
        self.assertEqual(26.5, p.transaction_cost)
        self.assertEqual(10.015, round(p.avg_price, 3))
        self.assertEqual(2400, p.volume)
        self.assertEqual(1900, p.frozen_volume)
        self.assertEqual(36.5, p.all_transaction_cost)
        # sell超过 sellable
        self.assertEqual((4992.5, 10, 500),
                         p.order_value(amount=-50000, price=10,
                                       current_cash=0.0))
        self.assertEqual(34.0, p.transaction_cost)
        self.assertEqual(10.023, round(p.avg_price, 3))
        self.assertEqual(1900, p.volume)
        self.assertEqual(1900, p.frozen_volume)
        self.assertEqual(44.0, p.all_transaction_cost)

    def test_order_basic(self):
        p = Portfolio(
            buy_commission_rate=0.001,
            sell_commission_rate=0.0015, min_commission=5.0,
            round_lot=100)
        p.update_before_trade(divide_rate=1.0)
        self.assertEqual((-10010.0, 10.0, 1000),
                         p._submit_order(side="buy", price=10.0, volume=1000))
        p.update_after_trade(close_price=10.0, cash_change=-10010,
                             pre_portfolio_value=30000.0)
        # test update_after_trade
        self.assertEqual(-10.0, p.daily_pnl)
        self.assertEqual(10000.0, p.market_value)
        self.assertEqual(-10.0, p.pnl)
        self.assertEqual(0.0, round(p.daily_return, 3))
        p.update_before_trade(divide_rate=1.0)

        # sell && buy
        # pecent = 0
        self.assertEqual((10983.5, 11, 1000),
                         p.order_target_percent(
                             percent=0, price=11,
                             pre_portfolio_value=29990.0,
                             current_cash=19990))
        self.assertEqual(16.5, p.transaction_cost)
        self.assertEqual(0, p.avg_price)
        self.assertEqual(0, p.volume)
        self.assertEqual(26.5, p.all_transaction_cost)
        # percent 0.5, 增仓
        self.assertEqual((-14014.0, 10, 1400),
                         p.order_target_percent(percent=0.5, price=10,
                                                pre_portfolio_value=29990.0,
                                                current_cash=30973.5))
        self.assertEqual(30.5, p.transaction_cost)
        self.assertEqual(10.01, p.avg_price)
        self.assertEqual(1400, p.volume)
        self.assertEqual(40.5, p.all_transaction_cost)
        # test update after trade
        p.update_after_trade(close_price=10.0, cash_change=10983.5-14014.0,
                             pre_portfolio_value=29990.0)
        self.assertEqual(969.5, p.daily_pnl)
        self.assertEqual(14000.0, p.market_value)
        self.assertEqual(959.5, p.pnl)
        self.assertEqual(0.03233, round(p.daily_return, 5))
        # next day, buy_hold, then sell
        p.update_before_trade(divide_rate=1.0)
        # percent 0.452, 保持不变
        p.order_target_percent(percent=0.452, price=10,
                               pre_portfolio_value=29990.0)
        self.assertEqual(0, p.daily_pnl)
        self.assertEqual(14000.0, p.market_value)
        self.assertEqual(959.5, p.pnl)
        self.assertEqual(0.0, round(p.daily_return, 5))
        p.update_after_trade(close_price=10.0, cash_change=0.0,
                             pre_portfolio_value=29990.0)
        # next day
        p.update_before_trade(divide_rate=1.0)
        # percent 0.35, 减仓700
        p.order_target_percent(percent=0.35, price=10,
                               pre_portfolio_value=20000.0)
        self.assertEqual(10.5, p.transaction_cost)
        self.assertEqual(10.035, p.avg_price)
        self.assertEqual(700, p.volume)
        self.assertEqual(51, p.all_transaction_cost)


if __name__ == '__main__':
    unittest.main()
