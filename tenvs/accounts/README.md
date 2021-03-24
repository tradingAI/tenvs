### 股票账户(StockAccount) 设计

每个bar只能提交一个订单:
- len(volumes) = len(codes) + 1
- volumes[i] > 0: 表示买入volumes[i]
- volumes[i] < 0: 表示卖出volumes[i]
- 需要调用方约束: 可用余额，可卖股票量限制, 以降低实际交易时的撤单率


向量化表示成份股的各种属性: 
- 优点: 使用numpy计算, 向量化操作, 代码少逻辑更清晰, 速度快, 适合回策阶段
- 缺点: 股票数据必需按照约定顺序组织， 交易量为0的股票即便不必更新计算，也需要进行按0值传入

股票账户的属性繁多，为了清晰表示实现的大致逻辑，将各属性需要更新的阶段用下表表示

|                      | day_init | order_execute | bar_settlement |
| -------------------- | -------- | ------------- | -------------- |
| pre_day_total_assets | 1        |               |                |
| prices               |          |               | 1              |
| caps                 |          |               | 2              |
| total_assets         |          |               | 3              |
| bar_pnl              |          |               | 4              |
| bar_pnls             |          |               | 5              |
| day_pnl              | 3        |               | 6              |
| day_pnls             | 4        |               | 7              |
| pnl                  |          |               | 8              |
| pnls                 |          |               | 9              |
| day_return           | 5        |               | 10             |
| day_returns          | 6        |               | 11             |
| value                |          |               | 12             |
| contributions        |          |               | 13             |
| weights              |          |               | 14             |
| day_fees             | 11       | 1             |                |
| day_fee              | 12       | 2             |                |
| fee                  |          | 3             |                |
| bar_cash_changes     |          | 4             |                |
| day_cash_changes     | 10       | 5             |                |
| balance              |          | 6             |                |
| available            | 7        | 7             |                |
| sellable_volumes     | 8        | 8             |                |
| frozen_volumes       | 9        | 9             |                |
| volumes              | 2        | 10            |                |
|                      |          |               |                |
|                      |          |               |                |
|                      |          |               |                |
|                      |          |               |                |