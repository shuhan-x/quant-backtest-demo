#动量因子得分高的股票，下个月是不是真的比得分低的股票涨得好？
#在每个月末，把股票按 mom_12_1 从大到小排序，平分成 5 组
#Group1是最看好的股票（动量最高）。
#Group5是最不看好的股票（动量最低）。
#如果策略有效，Group1的净值曲线应该高高在上，Group5应该垫底。两者的差值就是“多空收益”。

import pandas as pd
import matplotlib.pyplot as plt

# 解决画图时中文显示成方块的问题
plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows用黑体
plt.rcParams['axes.unicode_minus'] = False    # 正常显示负号

print("开始执行分层回测...")

# 1. 读取我们刚刚算好的因子数据
df = pd.read_csv('data/factor_data.csv')
df['date'] = pd.to_datetime(df['date'])

# 2. 每月按因子值大小分成 5 组
def assign_group(x):
    # qcut 会自动按分位数切分（前20%, 20%-40% ...）
    # labels=False 会返回 0,1,2,3,4，我们加 1 让它变成 1,2,3,4,5
    # 因为我们是动量因子，值越大越好，所以 Group 5 是因子最大的一组
    return pd.qcut(x, 5, labels=False, duplicates='drop') + 1

# 按月份分组，每个月单独排序分组
df['group'] = df.groupby('date')['mom_12_1'].transform(assign_group)

# 3. 计算每组的“等权平均收益”
# 也就是说，每个月把资金平分成5份，买入对应组的全部股票
group_returns = df.groupby(['date', 'group'])['next_month_ret'].mean().unstack()
print(group_returns.head())

# 4. 计算累计净值（把每月的收益率连乘起来）
# 比如连续两月收益是 10% 和 5%，净值就是 (1+0.1)*(1+0.05)
nav = (1 + group_returns).cumprod()

# 5. 画图展示
plt.figure(figsize=(10, 6))
for group in nav.columns:
    plt.plot(nav.index, nav[group], label=f'Group {group}')

plt.title('12-1 动量因子分层回测净值曲线')
plt.xlabel('日期')
plt.ylabel('累计净值')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)

# 保存图片到本地
plt.savefig('data/layered_nav.png', dpi=300, bbox_inches='tight')
print("回测图表已保存至 data/layered_nav.png")
plt.show()