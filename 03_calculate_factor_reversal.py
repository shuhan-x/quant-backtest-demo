import pandas as pd

print("开始计算 1 个月反转因子（修复版）...")
panel = pd.read_csv('data/panel.csv')
panel['date'] = pd.to_datetime(panel['date'])
panel['month'] = panel['date'].dt.to_period('M')

# 1. 核心修复：用 Tushare 自带的 pct_chg 计算每个月的真实收益（复利）
# pct_chg 是百分比，先除以 100，加 1 累乘，再减 1
monthly_ret = panel.groupby(['symbol', 'month'])['pct_chg'].apply(
    lambda x: (1 + x / 100).prod() - 1
).reset_index(name='month_ret')

# 2. 提取每个月最后一个交易日的数据（为了对齐日期）
monthly = panel.groupby(['symbol', 'month'], as_index=False).tail(1).copy()

# 3. 将真实收益率合并回月度表
monthly = pd.merge(monthly, monthly_ret, on=['symbol', 'month'], how='left')
monthly = monthly.sort_values(['symbol', 'date']).reset_index(drop=True)

# 4. 构造反转因子（上个月跌得越惨，得分越高）
monthly['factor_reversal'] = -monthly['month_ret']

# 5. 计算下个月真实收益（把下个月的 month_ret 挪上来）
monthly['next_month_ret'] = monthly.groupby('symbol')['month_ret'].shift(-1)

# 6. 清理空值
factor_data = monthly.dropna(subset=['factor_reversal', 'next_month_ret']).copy()

print(f"\n数据清洗后总行数: {len(factor_data)}")
factor_data.to_csv('data/factor_data_reversal.csv', index=False)
print("反转因子计算完成，已保存至 data/factor_data_reversal.csv！")