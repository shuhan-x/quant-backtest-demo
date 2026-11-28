import pandas as pd
import matplotlib.pyplot as plt
import numpy as np  # <--- 新增

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

print("开始执行反转因子分层回测（去极值版）...")
df = pd.read_csv('data/factor_data_reversal.csv')
df['date'] = pd.to_datetime(df['date'])

# 💡 核心修复：暴力去除极端收益（把大于 30% 的砍成 30%，小于 -30% 的砍成 -30%）
df['next_month_ret'] = np.clip(df['next_month_ret'], -0.3, 0.3)

def assign_group(x):
    return pd.qcut(x, 5, labels=False, duplicates='drop') + 1

df['group'] = df.groupby('date')['factor_reversal'].transform(assign_group)
group_returns = df.groupby(['date', 'group'])['next_month_ret'].mean().unstack()

nav = (1 + group_returns.fillna(0)).cumprod()

plt.figure(figsize=(10, 6))
for group in nav.columns:
    plt.plot(nav.index, nav[group], label=f'Group {group}')

plt.title('1个月反转因子分层回测净值曲线（去极值版）')
plt.xlabel('日期')
plt.ylabel('累计净值')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)

plt.savefig('data/layered_nav_reversal.png', dpi=300, bbox_inches='tight')
print("反转分层回测图表已保存！")
plt.show()