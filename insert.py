import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import sys

# ========== 数据库配置 ==========
DB_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'qwer963.',
    'host': '130.10.2.251',      # 或你的数据库 IP
    'port': '5434'            # 默认端口
}

# ========== Excel 文件路径 ==========
EXCEL_FILE = "消防点位绑定.xlsx"
SHEET_NAME = "Sheet1"

# ========== 表信息 ==========
TABLE_NAME = '"public"."iot_d_bind_device_info"'

def main():
    try:
        # 1. 读取 Excel
        print("正在读取 Excel 文件...")
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
        df.columns = df.columns.str.strip()  # 清理列名空格

        # 2. 校验必要字段
        required_columns = ['id', 'device_id', 'bind_device_id', 'bind_identifier', 'bind_explain']
        if not all(col in df.columns for col in required_columns):
            print("❌ Excel 缺少必要字段！必须包含：", required_columns)
            sys.exit(1)

        # 3. 转换数据（确保 id 是整数）
        data = []
        for _, row in df.iterrows():
            try:
                id_val = int(row['id'])
            except (ValueError, TypeError):
                print(f"❌ 无效的 id 值: {row['id']}")
                sys.exit(1)
            data.append((
                id_val,
                str(row['device_id']),
                str(row['bind_device_id']),
                str(row['bind_identifier']),
                str(row['bind_explain'])
            ))

        print(f"✅ 成功加载 {len(data)} 条记录")

        # 4. 连接数据库并插入
        print("正在连接数据库...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        insert_sql = f'''
            INSERT INTO {TABLE_NAME}
            ("id", "device_id", "bind_device_id", "bind_identifier", "bind_explain")
            VALUES (%s, %s, %s, %s, %s)
        '''

        print("正在插入数据...")
        execute_batch(cur, insert_sql, data, page_size=1000)
        conn.commit()

        print(f"✅ 成功插入 {len(data)} 条记录到 {TABLE_NAME}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")
        sys.exit(1)

    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()