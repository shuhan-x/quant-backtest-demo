import os
import tushare as ts
import pandas as pd
import time
import random
from dotenv import load_dotenv

# 1. 加载环境变量
load_dotenv(override=True, encoding='utf-8-sig')
token = os.getenv("TUSHARE_TOKEN")
pro = ts.pro_api(token)
pro._DataApi__http_url = "http://tus.sxdata.top/tu_share/"

if not os.path.exists('data/raw_tushare'):
    os.makedirs('data/raw_tushare')

# 2. 获取（或读取）全量成分股名单
cache_file = 'data/hs300_stocks_cache.csv'
all_stocks = []

if os.path.exists(cache_file):
    print("✅ 读取本地缓存的成分股名单...")
    all_stocks = pd.read_csv(cache_file)['ts_code'].tolist()
else:
    print("首次运行，拉取历史成分股名单（如果报错，请等5分钟重试）...")
    max_retries = 3
    for attempt in range(max_retries):
        try:
            hs300_weights = pro.index_weight(index_code='399300.SZ', start_date='20200101', end_date='20231231')
            all_stocks = hs300_weights['con_code'].unique().tolist()
            pd.DataFrame({'ts_code': all_stocks}).to_csv(cache_file, index=False)
            print(f"🎉 成功获取！共有 {len(all_stocks)} 只股票。")
            break
        except Exception as e:
            print(f"⚠️ 获取失败: {e}，等待 10 秒后重试...")
            time.sleep(10)

    if not all_stocks:
        print("❌ 彻底失败，服务器可能把你拉黑了，休息一会再来吧。")
        exit()

# 3. 全量下载（不怕它报错，断点续传会救我们）
test_stocks = all_stocks
print(f"🔥 目标：全量下载 {len(test_stocks)} 只股票！这将是一场持久战...")
print("💡 提示：你可以随时按 Ctrl+C 停止，下次运行会继续断点续传。")

success_count = 0
fail_count = 0

try:
    for index, ts_code in enumerate(test_stocks):
        file_path = f"data/raw_tushare/{ts_code}.csv"

        # 断点续传：如果存在且大于 1KB，直接跳过
        if os.path.exists(file_path) and os.path.getsize(file_path) > 1024:
            continue

        print(f"[{index + 1}/{len(test_stocks)}] 正在下载 {ts_code}...")

        for attempt in range(3):
            try:
                df = ts.pro_bar(api=pro, ts_code=ts_code, adj='hfq', start_date='20200101', end_date='20231231')

                if df is not None and not df.empty:
                    df = df.sort_values('trade_date').reset_index(drop=True)
                    df.to_csv(file_path, index=False)
                    print(f"  --> ✅ 成功保存 {ts_code}")
                    success_count += 1
                    break
                else:
                    print(f"  --> 警告: {ts_code} 数据为空")
                    break

            except Exception as e:
                if "请求速度过快" in str(e) or "ERROR" in str(e):
                    print(f"  --> ⚠️ 被限流了，罚站 10 秒... ({attempt + 1}/3)")
                    time.sleep(10)
                else:
                    print(f"  --> 其他报错: {e}")
                    fail_count += 1
                    break

        # 💡 核心防封：随机休眠 1.5 到 3.5 秒。让服务器觉得你是真人在操作
        time.sleep(random.uniform(1.5, 3.5))

except KeyboardInterrupt:
    print("\n🛑 你手动停止了下载。已完成的数据已经安全保存，下次运行会继续！")

print(f"\n🏁 本次下载结束！新增成功: {success_count} 只，失败: {fail_count} 只。")