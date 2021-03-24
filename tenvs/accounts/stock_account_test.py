import sys

import numpy as np
import pytest
from tenvs.accounts.stock_account import StockAccount


def mock_bars(day_num=10):
    closes1 = np.reshape(np.linspace(10.0, 11, day_num + 1), (day_num + 1, 1))
    closes2 = np.reshape(np.linspace(10.0, 11, day_num + 1), (day_num + 1, 1))
    closes3 = np.ones((day_num + 1, 1))
    closes = np.concatenate([closes1, closes2, closes3], axis=1)
    bars = {}
    for day in range(day_num):
        bars[str(day)] = {
            'pre_day_close': closes[day, :],
            'pre_bar_closes': closes[day, :],
            'closes': closes[day + 1, :],
            'opens': closes[day, :]}
    return bars


class TestStockAccount:

    def test_basic(self):
        np.random.seed(0)
        investment = 1e5
        codes = ['000001.SZ', '000001.SZ']
        account = StockAccount(investment, codes)
        assert account.investment == investment
        assert account.pre_day_total_assets == investment
        assert account.caps.tolist() == [0, 0, investment]
        assert account.total_assets == investment
        assert account.bar_pnl == 0.0
        assert account.bar_pnls.tolist() == [0.0, 0.0, 0.0]
        assert account.day_pnl == 0.0
        assert account.day_pnls.tolist() == [0.0, 0.0, 0.0]
        assert account.pnl == 0.0
        assert account.pnls.tolist() == [0.0, 0.0, 0.0]
        assert account.day_return == 0
        assert account.day_returns.tolist() == [0.0, 0.0, 0.0]
        assert account.value == 1.0
        assert account.contributions.tolist() == [0.0, 0.0, 0.0]
        assert account.weights.tolist() == [0.0, 0.0, 1.0]
        assert account.day_fee == 0
        assert account.day_fees.tolist() == [0.0, 0.0, 0.0]
        assert account.fee == 0
        assert account.bar_cash_changes.tolist() == [0.0, 0.0, 0.0]
        assert account.day_cash_changes.tolist() == [0.0, 0.0, 0.0]
        assert account.balance == investment
        bars = mock_bars(10)
        # 各买入500股
        day = '0'
        volumes = np.array([500, 500, 0])
        account.bar_execute(
            volumes=volumes, bar=bars[day], bar_id=0, day_log=True, day=day)
        assert account.available == 89990.0
        assert account.pre_day_total_assets == investment
        assert account.caps.tolist() == [5050.0, 5050.0, 89990.0]
        assert account.total_assets == 100090.0
        assert account.bar_pnl == 90.0
        assert account.bar_pnls.tolist() == [45.0, 45.0, 0.0]
        assert account.day_pnl == 90.0
        assert account.day_pnls.tolist() == [45.0, 45.0, 0.0]
        assert account.day_pnl == 90.0
        assert account.day_pnls.tolist() == [45.0, 45.0, 0.0]
        assert account.day_return == 0.0009
        assert account.day_returns.tolist() == [0.00045, 0.00045, 0.0]
        assert account.value == 1.0009
        assert account.contributions.tolist() == [0.00045, 0.00045, 0.0]
        assert account.weights.tolist() == [
            0.0504545908682186, 0.0504545908682186, 0.8990908182635627]
        assert account.day_fee == 10.0
        assert account.day_fees.tolist() == [5.0, 5.0, 0.0]
        assert account.fee == 10.0
        assert account.bar_cash_changes.tolist(
        ) == [-5005.0, -5005.0, -10010.0]
        assert account.day_cash_changes.tolist(
        ) == [-5005.0, -5005.0, -10010.0]
        assert account.balance == 89990.00
        assert account.available == 89990.00
        assert account.sellable_volumes.tolist() == [0., 0., 89990.0]
        assert account.frozen_volumes.tolist() == [500., 500., 0.]
        assert account.volumes.tolist() == [500., 500., 89990.0]
        # 再次买入
        volumes = np.array([6000, 500, 0])
        day = '1'
        account.bar_execute(
            volumes=volumes, bar=bars[day], bar_id=0, day_log=True, day=day)
        assert account.available == 24330.0
        assert account.pre_day_total_assets == 100090.0
        assert account.caps.tolist() == [66300.0, 10200.0, 24330.0]
        assert account.total_assets == 100830.0
        assert account.bar_pnl == 740.0
        assert account.bar_pnls.tolist() == [645.0, 95.0, 0.0]
        assert account.day_pnl == 740.0
        assert account.day_pnls.tolist() == [645.0, 95.0, 0.0]
        assert account.day_pnl == 740.0
        assert account.day_pnls.tolist() == [645.0, 95.0, 0.0]
        assert account.day_return == 0.007393345988610251
        assert account.day_returns.tolist(
        ) == [0.006444200219802178, 0.0009491457688080727, 0.0]
        assert account.value == 1.0083
        assert account.contributions.tolist() == [0.0069, 0.0014, 0.0]
        assert account.weights.tolist() == [
            0.6575423980958048, 0.10116036893781613, 0.24129723296637906]
        assert account.day_fee == 10.0
        assert account.day_fees.tolist() == [5.0, 5.0, 0.0]
        assert account.fee == 20.0
        assert account.bar_cash_changes.tolist(
        ) == [-60605.0, -5055.0, -65660.0]
        assert account.day_cash_changes.tolist(
        ) == [-60605.0, -5055.0, -65660.0]
        assert account.balance == 24330.0
        assert account.available == 24330.0
        assert account.sellable_volumes.tolist() == [500.0, 500.0, 24330.0]
        assert account.frozen_volumes.tolist() == [6000.0, 500.0, 0.0]
        assert account.volumes.tolist() == [6500.0, 1000.0, 24330.0]
        # 卖出
        volumes = np.array([-5000, 500, 0])
        day = '2'
        account.bar_execute(
            volumes=volumes, bar=bars[day], bar_id=0, day_log=True, day=day)
        assert account.available == 70129.222
        assert account.pre_day_total_assets == 100830.0
        assert account.caps.tolist() == [15450.0, 15450.0, 70129.222]
        assert account.total_assets == 101029.222
        assert account.bar_pnl == 199.222
        assert account.bar_pnls.tolist() == [
            54.222, 145.0, 0.0]
        assert account.day_pnl == 199.222
        assert account.day_pnls.tolist() == [
            54.222, 145.0, 0.0]
        assert account.day_pnl == 199.222
        assert account.day_pnls.tolist() == [
            54.222, 145.0, 0.0]
        assert account.day_return == 0.0019758206882872164

        assert account.day_returns.tolist(
        ) == [0.0005377566200535555, 0.0014380640682336607, 0.0]
        assert account.value == 1.01029222
        assert account.contributions.tolist() == [0.00744222, 0.00285, 0.0]
        assert account.weights.tolist() == [
            0.1529260514349007, 0.1529260514349007, 0.6941478971301986]

        assert account.day_fee == 100.778
        assert account.day_fees.tolist() == [95.778, 5.0, 0.0]
        assert account.fee == 120.778

        assert account.bar_cash_changes.tolist(
        ) == [50904.222, -5105.0, 45799.222]
        assert account.day_cash_changes.tolist(
        ) == [50904.222, -5105.0, 45799.222]
        assert account.balance == 70129.222
        assert account.available == 70129.222

        assert account.sellable_volumes.tolist(
        ) == [1500.0, 1000.0, 24330.0]
        assert account.frozen_volumes.tolist() == [0.0, 500.0, 45799.222]
        assert account.volumes.tolist() == [1500.0, 1500.0, 70129.222]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
