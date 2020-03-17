# -*- coding:utf-8 -*-
from tenvs.logger import logger

mapping = {}


def register(name):
    def _thunk(func):
        mapping[name] = func
        return func
    return _thunk


@register("simple")
def simple(daily_return, *args):
    if daily_return <= 0:
        return -1
    else:
        return 1


def daily_return(daily_return, *args):
    return daily_return


@register("daily_return_add_count_rate")
def daily_return_add_count_rate(daily_return, highs, lows,
                                closes, sell_prices, buy_prices):
    fail, success, profit_count, loss_count = 0, 0, 0
    for i in range(len(highs)):
        # 买
        if buy_prices[i] >= lows[i]:
            success += 1
            if buy_prices[i] <= closes[i]:
                profit_count += 1
            else:
                loss_count += 1
        else:
            fail += 1

        # 卖
        if sell_prices[i] <= highs[i]:
            success += 1
            if sell_prices[i] <= closes[i]:
                loss_count += 1
            else:
                profit_count += 1
        else:
            fail += 1

    success_rate = (success * 2) / (success + fail)
    profit_rate = (profit_count * 2) / (profit_count + loss_count)

    reward = daily_return + success_rate + profit_rate

    return reward


def mean_squared_error(a, b, scaled=10.0):
    """
    arguments:
        a: list of values
        b: list of values
        scaled: 误差调整倍率
    return:
        mean squared error
    """
    v = 0.0
    n = len(a)
    for i in range(n):
        if a[i] != 0:
            v += (scaled * (1 - b[i] / a[i])) ** 2
    return v / n


@register("daily_return_add_buy_sell_penalty")
def daily_return_add_buy_sell_penalty(daily_return, highs, lows,
                                      closes, sell_prices, buy_prices):
    reward = daily_return
    n = len(highs)
    # 如果出现买价>卖价 增加一个较大的惩罚
    for i in range(n):
        if sell_prices[i] < buy_prices[i]:
            reward -= 0.05
    reward = reward * 3
    return reward


@register("daily_return_add_price_bound")
def daily_return_add_price_bound(daily_return, highs, lows,
                                 closes, sell_prices, buy_prices):
    reward = daily_return
    n = len(highs)
    # 如果出现买价>卖价 增加一个较大的惩罚
    for i in range(n):
        if sell_prices[i] < buy_prices[i]:
            reward -= 1.0
    # 计算 bound
    sell_error = mean_squared_error(highs, sell_prices)
    buy_error = mean_squared_error(lows, buy_prices)

    reward = reward - sell_error - buy_error
    return reward


@register("daily_return_with_chl_penalty")
def daily_return_with_chl_penalty(daily_return, highs, lows,
                                  closes, sell_prices, buy_prices):
    reward = daily_return_add_price_bound(daily_return, highs, lows, closes,
                                          sell_prices, buy_prices)
    # 增加相对于收盘价的惩罚
    close_error_sum = 0
    n = len(highs)
    for i in range(n):
        if closes[i] == 0:
            continue
        if sell_prices[i] < closes[i]:
            close_error = (closes[i] - sell_prices[i]) * 10 / closes[i]
            close_error_sum += close_error ** 2
        if buy_prices[i] > closes[i]:
            close_error = (buy_prices[i] - closes[i]) * 10 / closes[i]
            close_error_sum += close_error ** 2
    reward = reward + close_error_sum
    return reward


def get_reward_func(name):
    """
    If you want to register your own reward function, you just need:
    Usage Example:
    -------------
    from tenvs.envs.reward import register
    @register("your_reward_function_name")
    def your_reward_function(**kwargs):
        ...
        return reward_fn
    """
    logger.info("tenvs.envs.reward use reward function: %s" % name)
    if callable(name):
        return name
    elif name in mapping:
        return mapping[name]
    else:
        raise ValueError('Unknown network type: {}'.format(name))


def main():
    r_func = get_reward_func(name="simple")
    assert -1 == r_func(0)
    assert 1 == r_func(0.01)
    assert -1 == r_func(-0.01)


if __name__ == '__main__':
    main()
