import unittest

from tenvs.envs.reward import get_reward_func, mean_squared_error


class TestReward(unittest.TestCase):
    def test_mean_squared_error(self):
        a = [2.0, 4.0]
        b = [1.0, 4.0]
        mse = mean_squared_error(a, b)
        self.assertEqual(12.5, mse)

    def test_daily_return_add_price_bound(self):
        fn = get_reward_func("daily_return_add_price_bound")
        highs, lows, closes = [100], [90], [95]
        sell_prices, buy_prices = [98], [92]
        v = fn(0.03, highs, lows, closes, sell_prices, buy_prices)
        self.assertEqual(-0.05938271604938244, v)

    def test_daily_return_add_buy_sell_penalty(self):
        fn = get_reward_func("daily_return_add_buy_sell_penalty")
        highs, lows, closes = [100], [90], [95]
        sell_prices, buy_prices = [98], [92]
        v = fn(0.03, highs, lows, closes, sell_prices, buy_prices)
        self.assertEqual(0.09, v)


if __name__ == '__main__':
    unittest.main()
