import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
import numpy as np  # <--- 核心1：引入 numpy

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

print("开始计算反转因子IC和交易成本（去极值版）...")
df = pd.read_csv('data/factor_data_reversal.csv')
df['date'] = pd.to_datetime(df['date'])

# 💡 核心修复 2：暴力去除极端收益（和 04 里的操作一模一样）
df['next_month_ret'] = np.clip(df['next_month_ret'], -0.3, 0.3)

ic_list = []
for date, group in df.groupby('date'):
    if len(group) > 2:
        ic, _ = spearmanr(group['factor_reversal'], group['next_month_ret'])
        ic_list.append({'date': date, 'IC': ic})

ic_df = pd.DataFrame(ic_list)
ic_mean = ic_df['IC'].mean()
ic_std = ic_df['IC'].std()
ic_ir = ic_mean / ic_std

print(f"\n--- 反转因子评价指标 ---")
print(f"Rank IC 均值: {ic_mean:.4f}")
print(f"ICIR 值: {ic_ir:.4f}")

def assign_group(x):
    return pd.qcut(x, 5, labels=False, duplicates='drop') + 1

df['group'] = df.groupby('date')['factor_reversal'].transform(assign_group)
group_returns = df.groupby(['date', 'group'])['next_month_ret'].mean().unstack()

# 算多空（这里不会再有极其夸张的负数了）
long_short_gross = group_returns[5.0] - group_returns[1.0]
long_short_net = long_short_gross - 0.006

plt.figure(figsize=(10, 6))
plt.plot((1 + long_short_gross.fillna(0)).cumprod(), label='多空收益 (未扣费)', color='green', linewidth=2)
plt.plot((1 + long_short_net.fillna(0)).cumprod(), label='多空收益 (扣除交易成本)', color='red', linestyle='--', linewidth=2)

plt.title('反转因子多空对冲净值曲线（去极值版）')
plt.xlabel('日期')
plt.ylabel('累计净值')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)

plt.savefig('data/long_short_nav_reversal.png', dpi=300, bbox_inches='tight')
print("\n反转多空收益对比图已保存至 data/long_short_nav_reversal.png")
plt.show()