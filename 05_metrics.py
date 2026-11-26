import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

print("开始计算因子IC和交易成本...")

# 1. 读取因子数据
df = pd.read_csv('data/factor_data.csv')
df['date'] = pd.to_datetime(df['date'])

# ================= 第一部分：计算 Rank IC =================
# IC 是每个月，股票“因子得分”和“下个月收益”的秩相关系数（Spearman）
# 它衡量的是：因子排名越靠前，下个月赚得是不是真的越多
ic_list = []
for date, group in df.groupby('date'):
    # 剔除只有一个股票或者没数据的月份
    if len(group) > 2:
        ic, _ = spearmanr(group['mom_12_1'], group['next_month_ret'])
        ic_list.append({'date': date, 'IC': ic})

ic_df = pd.DataFrame(ic_list)
ic_mean = ic_df['IC'].mean()
ic_std = ic_df['IC'].std()
ic_ir = ic_mean / ic_std  # ICIR 是 IC 的均值除以标准差，衡量因子稳定性

print(f"\n--- 因子评价指标 ---")
print(f"Rank IC 均值: {ic_mean:.4f} (一般绝对值大于 0.03 算有效)")
print(f"ICIR 值: {ic_ir:.4f} (一般大于 0.3 算稳定)")

# ================= 第二部分：加入交易成本 =================
# 假设每月调仓，单边交易成本设为 0.15%（包含佣金、印花税、滑点）
cost_rate = 0.0015

def assign_group(x):
    return pd.qcut(x, 5, labels=False, duplicates='drop') + 1

df['group'] = df.groupby('date')['mom_12_1'].transform(assign_group)
group_returns = df.groupby(['date', 'group'])['next_month_ret'].mean().unstack()

# 计算扣费后的净值：每月收益率减去双边交易成本（假设每次调仓换手100%，所以扣双边）
# 为了严谨，我们简单点，每个组每月收益直接减去 0.15% * 2 = 0.3%
group_returns_net = group_returns - 0.003

# 去掉 NaN 填补 0，防止 cumprod 连乘中断
nav_gross = (1 + group_returns.fillna(0)).cumprod()
nav_net = (1 + group_returns_net.fillna(0)).cumprod()

# 画一张对比图，看看交易成本“吃掉”了多少收益
plt.figure(figsize=(10, 6))
# 画多空组合（G5 减去 G1）：最理想的收益
long_short_gross = group_returns[5.0] - group_returns[1.0]

# 多空策略的真实成本：买多 1 次（0.15%）+ 平仓 1 次（0.15%）+ 做空 1 次（0.15%）+ 平空 1 次（0.15%）= 0.6%
long_short_net = long_short_gross - 0.006

plt.plot((1 + long_short_gross.fillna(0)).cumprod(), label='多空收益 (未扣费)', color='green', linewidth=2)
plt.plot((1 + long_short_net.fillna(0)).cumprod(), label='多空收益 (扣除交易成本)', color='red', linestyle='--', linewidth=2)

plt.title('多空对冲净值曲线：交易成本的真实影响')
plt.xlabel('日期')
plt.ylabel('累计净值')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)

plt.savefig('data/long_short_nav.png', dpi=300, bbox_inches='tight')
print("\n多空收益对比图已保存至 data/long_short_nav.png")
plt.show()

print("\n项目全流程跑通！现在你可以去更新你的 README 了！")

#为什么图中红线和绿线完全重合了