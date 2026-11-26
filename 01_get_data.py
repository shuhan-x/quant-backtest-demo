import akshare as ak
import pandas as pd
import os
import time

if not os.path.exists('data/raw'):
    os.makedirs('data/raw')

print("正在获取沪深300成分股列表...")
hs300_df = ak.index_stock_cons_csindex(symbol="000300")
stock_list = hs300_df['成分券代码'].astype(str).str.zfill(6).tolist()

# 目标下载前 100 只
test_stocks = stock_list[:100]
print(f"计划下载 {len(test_stocks)} 只股票的数据...")

for symbol in test_stocks:
    file_path = f"data/raw/{symbol}.csv"

    # 已经有文件的，直接跳过
    if os.path.exists(file_path):
        print(f"跳过 {symbol} (已存在)")
        continue

    print(f"正在下载 {symbol} 的数据...")
    try:
        df = ak.stock_zh_a_hist_em(
            symbol=symbol,
            period="daily",
            start_date="20180101",
            end_date="20241231",
            adjust="hfq"
        )

        if not df.empty:
            df.to_csv(file_path, index=False)
            print(f"  --> 成功保存 {symbol}")
        else:
            print(f"  --> 警告: {symbol} 数据为空")

    except Exception as e:
        print(f"  --> 下载 {symbol} 失败, 报错信息: {e}")

    # 注意看这里！！！和 try 对齐，不管成功失败都强制睡 2 秒！
    time.sleep(2)

print("全部下载任务执行完毕！")