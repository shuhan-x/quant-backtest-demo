import pandas as pd
import glob
import os

print("开始构建面板数据...")

# 1. 自动找到 data/raw 文件夹下所有的 csv 文件
file_list = glob.glob("data/raw/*.csv")

if not file_list:
    print("错误：没找到数据，请先运行 01_get_data.py")
else:
    all_data = []

    # 2. 循环读取每个文件
    for file in file_list:
        # 从文件名提取股票代码，比如 data/raw/600519.csv 提取出 600519
        symbol = os.path.basename(file).replace('.csv', '')

        # 读取数据
        df = pd.read_csv(file)

        # 在数据里增加一列“股票代码”
        df['symbol'] = symbol

        all_data.append(df)

    # 3. 将 n 个表格上下拼接到一起
    panel = pd.concat(all_data, ignore_index=True)

    # 4. 统一列名（把中文表头改成英文，防止以后写代码报错）
    # 注意：不同的接口返回的列名可能不同，这里做了一个常见中英文映射
    rename_dict = {
        '日期': 'date',
        '开盘': 'open',
        '收盘': 'close',
        '最高': 'high',
        '最低': 'low',
        '成交量': 'volume',
        '成交额': 'amount'
    }
    panel = panel.rename(columns=rename_dict)

    # 5. 把日期变成标准时间格式，并按“日期+股票代码”排序
    panel['date'] = pd.to_datetime(panel['date'])
    panel = panel.sort_values(by=['date', 'symbol']).reset_index(drop=True)

    # 6. 检查一下拼好的数据
    print("\n合并完成！数据预览（前5行）：")
    print(panel.head())

    print(f"\n数据总行数: {len(panel)}，共包含 {panel['symbol'].nunique()} 只股票")

    # 7. 保存成一张大表
    panel.to_csv("data/panel.csv", index=False)
    print("\n大表已成功保存至 data/panel.csv，可以进入第三步了！")