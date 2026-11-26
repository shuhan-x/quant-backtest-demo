import pandas as pd

print("开始计算 12-1 动量因子...")

# 1. 读取刚合并好的面板数据
panel = pd.read_csv('data/panel.csv')
panel['date'] = pd.to_datetime(panel['date'])

# 2. 提取每个月最后一个交易日的数据（月末快照）
# 新增 month 列（如 2020-01），然后按股票和月份分组，取最后一天
panel['month'] = panel['date'].dt.to_period('M')
monthly = panel.groupby(['symbol', 'month'], as_index=False).tail(1).copy()

# 按股票和日期排序，确保计算顺序正确
monthly = monthly.sort_values(['symbol', 'date']).reset_index(drop=True)

# 3. 计算 12-1 月动量因子
# 公式：1个月前的收盘价 / 12个月前的收盘价 - 1
# transform 会自动按股票分组，避免股票之间数据串在一起
monthly['mom_12_1'] = monthly.groupby('symbol')['close'].transform(
    lambda x: x.shift(1) / x.shift(12) - 1
)

# 4. 计算“下个月收益率”（这是我们要预测的目标）
# 下个月收益 = 下个月末收盘价 / 本月末收盘价 - 1
monthly['next_month_ret'] = monthly.groupby('symbol')['close'].transform(
    lambda x: x.shift(-1) / x - 1
)

# 5. 清理数据
# 刚上市的股票前面没有12个月数据，会有空值，直接删掉
factor_data = monthly.dropna(subset=['mom_12_1', 'next_month_ret']).copy()

# 6. 打印预览看效果
print("\n因子数据预览（包含：日期, 代码, 动量因子, 下月收益）：")
print(factor_data[['date', 'symbol', 'mom_12_1', 'next_month_ret']].head())

print(f"\n数据清洗后总行数: {len(factor_data)}")

# 7. 保存文件
factor_data.to_csv('data/factor_data.csv', index=False)
print("\n因子计算完成，已保存至 data/factor_data.csv！")

#备注：“12-1 月动量因子”：过去 12 个月的收益率，但剔除了最近 1 个月。
#研究发现，短期（最近一个月）往往存在“反转效应”（涨多了会跌）。
#为了简化回测，采用月度调仓