# -*- coding:utf-8 -*-

from tenvs.logger import logger


class Portfolio:
    """
    NOTE: 考虑到不同的类型的资产commission并不一样, 所以Portfolio需要commission相关的参
    数
    divide_rate_threshold: 是否有拆分判断阀值
    """

    def __init__(self,
                 buy_commission_rate=0.001, sell_commission_rate=0.0015,
                 min_commission=5.0, round_lot=100,
                 divide_rate_threshold=1.005, code="000001.SZ",
                 log_deals=False):
        # 市值
        self.market_value = 0.0
        # 持仓量
        self.volume = 0
        # 前一持仓量
        self.pre_volume = 0
        # 冻结量
        self.frozen_volume = 0
        # 该仓位可卖出股数。T＋1 的市场中sellable = 所有持仓 - 已冻结
        self.sellable = 0
        # 平均开仓价格
        self.avg_price = 0.0
        # 最近一次成交的价格
        self._price = 0.0
        # 当日盈亏
        self.daily_pnl = 0.0
        # 累计盈亏, Profit and Loss
        self.pnl = 0.0
        # 当前最新一天的日收益率, 以总账户为基线
        self.daily_return = 0.0
        # 当日交易费
        self.transaction_cost = 0.0
        # 累计交易费
        self.all_transaction_cost = 0.0
        # 获得该持仓的市场价值在股票投资组合价值中所占比例，取值范围[0, 1], 以总账户为基线
        self.value_percent = 0.0
        # 是否停牌, 停牌为1
        self.is_suspended = 0.0
        # 买入佣金率
        self.buy_commission_rate = buy_commission_rate
        # 卖佣金率
        self.sell_commission_rate = sell_commission_rate
        # 单笔最低佣金
        self.min_commission = min_commission
        # 一手对应多少股，中国A股一手是100股
        self.round_lot = round_lot
        self.divide_rate_threshold = divide_rate_threshold
        self.code = code
        # 是否打印订单记录
        self.log_deals = log_deals

    def update_value_percent(self, total_value):
        """
        [float] 获得该持仓的实时市场价值在股票投资组合价值中所占比例，取值范围[0, 1]
        """
        if total_value == 0:
            self.value_percent = 0
        else:
            self.value_percent = self.market_value / total_value

    def _buy_fee(self, amount):
        # 1.印花税：由卖方出
        # 2.证管费：约为成交金额的0.00002收取
        # 3.证券交易经手费：A股，按成交金额的0.00696%收取
        # A股2、3项收费合计称为交易规费，合计收取成交金额的0.00896%，包含在券商交易佣金中。
        # 4.过户费: 按成交金额的0.002%收取。
        # 5.券商交易佣金：最高不超过成交金额的3‰，最低5元起，单笔交易佣金不满5元按5元收取。
        # NOTE: 实际操作费率约： 0.0010775285
        return round(max(self.min_commission,
                         amount * self.buy_commission_rate), 2)

    def _sell_fee(self, amount):
        # 1.印花税：成交金额的 0.001, 2008年9月19日至今由向双边征收改为向出让方单边征收
        # 2.证管费：约为成交金额的0.00002收取
        # 3.证券交易经手费：A股，按成交金额的0.00696%收取
        # A股2、3项收费合计称为交易规费，合计收取成交金额的0.00896%，包含在券商交易佣金中。
        # 4.过户费: 按成交金额的0.002%收取。
        # 实际操作费率： 0.00126019
        return round(amount * self.sell_commission_rate, 2)

    def buy(self, price, volume):
        # 买入
        amount = volume * price
        transaction_cost = self._buy_fee(amount)
        self.transaction_cost += transaction_cost
        # 平均开仓价更新
        self.avg_price = (self.avg_price * self.volume +
                          amount + transaction_cost) / (self.volume + volume)
        self._price = price
        self.volume += volume
        self.frozen_volume += volume
        self.all_transaction_cost += transaction_cost
        cash_change = -amount - transaction_cost
        if self.log_deals and volume > 0:
            logger.info("buy %s price: %.3f, volume: %d" % (self.code,
                                                            price, volume))
        logger.debug("buy %s price: %.3f, volume: %d" % (self.code,
                                                         price, volume))
        return cash_change, price, volume

    def is_divide(self, divide_rate):
        # 拆分判断, 有拆分返回 True, 否则 False
        return divide_rate > self.divide_rate_threshold

    def update_before_trade(self, divide_rate):
        # 如果有拆分
        if self.is_divide(divide_rate):
            logger.debug("update_before_trade: %s divide_rate: %.3f" % (
                self.code, divide_rate))
            self.volume = int(divide_rate * self.volume)
        self.sellable = self.volume
        self.frozen_volume = 0
        self.daily_pnl = 0.0
        self.daily_return = 0.0
        self.transaction_cost = 0.0
        self.pre_volume = self.volume

    def sell(self, price, volume):
        # 卖出
        amount = volume * price
        transaction_cost = self._sell_fee(amount)
        # 平均开仓价更新
        if self.volume == volume:
            self.avg_price = 0.0
        else:
            self.avg_price = (self.avg_price * self.volume - amount +
                              transaction_cost) / (self.volume - volume)
        self._price = price
        self.transaction_cost += transaction_cost
        self.volume -= volume
        self.sellable -= volume
        self.all_transaction_cost += transaction_cost
        cash_change = amount - transaction_cost
        if self.log_deals and volume > 0:
            logger.info("sell %s price: %.3f, volume: %d" % (self.code,
                                                             price, volume))
        logger.debug("sell %s price: %.3f, volume: %d" % (self.code,
                                                          price, volume))
        return cash_change, price, volume

    def _submit_order(self, side=None, price=None, volume=None):
        logger.debug("portfolio: submit_order %s, %4s, %5.2f, %6d" % (
            self.code, side, price, volume))
        if side == "sell":
            return self.sell(price=price, volume=volume)
        elif side == "buy":
            return self.buy(price=price, volume=volume)

    def _sell_all_stock(self, price):
        if self.sellable == 0:
            logger.debug("%s sell_all_stock sellable is 0" % self.code)
        return self._submit_order(side="sell", price=price,
                                  volume=self.sellable)

    def order_value(self, amount, price, current_cash):
        """
        使用想要花费的金钱买入/卖出股票，而不是买入/卖出想要的股数，正数代表买入，负数代表卖出
        股票的股数总是会被调整成对应的100的倍数（在A中国A股市场1手是100股）
        如果资金不足，将不会创建发送订单
        需要注意：
        当您提交一个买单时，cash_amount 代表的含义是您希望买入股票消耗的金额（包含税费），
        最终买入的股数不仅和发单的价格有关，还和税费相关的参数设置有关。
        当您提交一个卖单时，cash_amount 代表的意义是您希望卖出股票的总价值。
        如果金额超出了您所持有股票的价值，那么您将卖出所有股票。
        :example:
        .. code-block:: python
            #花费最多￥10000买入平安银行股票，并以市价单发送。具体下单的数量与您策略税费相关
            的配置有关。
            order_value('000001.XSHE', 10000)
            #卖出价值￥10000的现在持有的平安银行：
            order_value('000001.XSHE', -10000)
        """
        if amount > 0:
            amount = min(amount, current_cash)
            volume = int(amount / (price * self.round_lot)) * self.round_lot
            while volume > 0:
                amount = volume * price
                expected_transaction_cost = self._buy_fee(amount)
                if amount + expected_transaction_cost <= current_cash:
                    break
                volume -= self.round_lot
            if volume > 0:
                return self._submit_order("buy", price, volume)
            if volume == 0:
                logger.debug("order_value failed: 0 order quantity")
                return 0, 0, 0

        elif amount < 0:
            vol = int(amount / (price * self.round_lot)) * self.round_lot
            volume = abs(vol)
            # 根据可卖出股数, 按最大可交易量，调整
            volume = min(self.sellable, volume)
            return self._submit_order(side="sell", price=price, volume=volume)
        else:
            return 0, 0, 0

    def order_target_percent(self, percent=None, price=None,
                             pre_portfolio_value=None, current_cash=None):
        """
        NOTE: 在调用之前，应该确定price是可以交易的，这里不对交易量进行限制.
        买入/卖出证券以自动调整该证券的仓位到占有一个目标价值.
        加仓时，percent 代表证券已有持仓的价值加上即将花费的现金（包含税费）的总值占当前投资
        组合总价值的比例。
        减仓时，percent 代表证券将被调整到的目标价至占当前投资组合总价值的比例。
        投资组合价值等于所有已有仓位的价值和剩余现金的总和。
        买/卖单会被下舍入一手股数（A股是100的倍数）的倍数。目标百分比应该是一个小数，
        并且最大值应该<=1，比如0.5表示50%。
        如果position_to_adjust 计算之后是正的，那么会买入该证券，否则会卖出该证券.
        需要注意，如果资金不足，该API将不会创建发送订单.
        """
        if percent < 0 or percent > 1:
            raise Exception(u"percent should between 0 and 1")
            return 0

        if percent == 0:
            return self._sell_all_stock(price)
        # portfolio_value 为上一交易日的值，并没有在每笔交易时更新，
        # 所以实时交易时，这里需要调整为实时的 portfolio_value
        adjust = pre_portfolio_value * percent - self.volume * self._price
        return self.order_value(adjust, price, current_cash)

    def update_after_trade(self, close_price, cash_change,
                           pre_portfolio_value):
        # 昨日收盘市值
        pre_market_value = self.market_value
        # 收盘后，根据收盘价更新
        self.market_value = self.volume * close_price
        self.daily_pnl = self.market_value - pre_market_value + cash_change
        self.pnl += self.daily_pnl

        if pre_portfolio_value == 0:
            self.daily_return = 0
        else:
            self.daily_return = self.daily_pnl / pre_portfolio_value
