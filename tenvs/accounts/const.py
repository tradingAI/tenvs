# 交易量为100整数倍
ROUND_LOT = 100

'''
以万 2.5 佣金结构为例
深证证券交易所
项目	费用	收取部门
过户费	万 0.2	由中国结算收取
证管费	万 0.2	由证监会收取
经手费	万 0.487	由交易所收取
券商收入	万 1.613	由券商收取

上海证券交易所
项目	费用	收取部门
证管费	万 0.2	由证监会收取
经手费	万 0.487	由交易所收取
券商收入	万 1.813	由券商收取

印花税: (卖出)千1
佣金: 最高千3, 单笔最低5， (双向)万0.878
'''
STK_BUY_COMMISSION_RATE = 0.000878
STK_SELL_COMMISSION_RATE = 0.001878
MIN_COMMISSION = 5.0

# 空仓, 股票代号
MONEY = 'RMB'
MONEY_PRICE = 1.0
# 开市
TRADE = 1
# 休市
STOP = 0
