import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import sys

# ========== 数据库配置 ==========
DB_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'qwer963.',
    'host': '130.10.2.251',
    'port': '5434'
}

EXCEL_FILE = "消防点位绑定.xlsx"
SHEET_NAME = "二号楼"
TABLE_NAME = '"public"."iot_d_bind_device_info"'
DEFAULT_START_ID = 1985245409940512930


def safe_split(value):
    if pd.isna(value) or str(value).strip() == '':
        return []
    return [x.strip() for x in str(value).split(',') if x.strip()]


def expand_row(row):
    # 拆分四组
    devs = safe_split(row['device_id'])
    explains = safe_split(row['bind_explain'])
    cams = safe_split(row['bind_device_id'])
    idens = safe_split(row['bind_identifier'])

    # 校验：device_id 和 bind_explain 必须等长
    if len(devs) != len(explains):
        raise ValueError(f"device_id ({len(devs)}) 与 bind_explain ({len(explains)}) 数量必须一致")

    # 校验：bind_device_id 和 bind_identifier 必须等长
    if len(cams) != len(idens):
        raise ValueError(f"bind_device_id ({len(cams)}) 与 bind_identifier ({len(idens)}) 数量必须一致")

    if not devs or not cams:
        return []

    records = []
    # 笛卡尔积：每个 (dev, explain) × 每个 (cam, iden)
    for dev, exp in zip(devs, explains):
        for cam, iden in zip(cams, idens):
            records.append((dev, cam, iden, exp))
    return records


def main():
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
        df.columns = df.columns.str.strip()

        required = ['device_id', 'bind_device_id', 'bind_identifier', 'bind_explain']
        if not all(col in df.columns for col in required):
            print(f"❌ 缺少必要列: {required}")
            sys.exit(1)

        # 确定起始 ID（基于 Excel 中已有 id 最大值）
        if 'id' in df.columns and df['id'].notnull().any():
            valid_ids = pd.to_numeric(df['id'], errors='coerce').dropna()
            max_id = int(valid_ids.max()) if not valid_ids.empty else DEFAULT_START_ID - 1
        else:
            max_id = DEFAULT_START_ID - 1

        start_id = max_id + 1
        print(f"基础 id: {max_id}，新记录从 {start_id} 开始")

        # 展开所有行
        all_records = []
        for _, row in df.iterrows():
            if pd.isna(row['device_id']) or pd.isna(row['bind_device_id']):
                continue
            all_records.extend(expand_row(row))

        print(f"✅ 展开后共 {len(all_records)} 条记录")

        # 生成带 id 的数据
        data = [
            (start_id + i, dev, cam, iden, exp)
            for i, (dev, cam, iden, exp) in enumerate(all_records)
        ]

        # 插入数据库
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        insert_sql = f'''
            INSERT INTO {TABLE_NAME}
            ("id", "device_id", "bind_device_id", "bind_identifier", "bind_explain")
            VALUES (%s, %s, %s, %s, %s)
        '''
        execute_batch(cur, insert_sql, data, page_size=1000)
        conn.commit()
        cur.close()
        conn.close()

        print(f"✅ 成功插入 {len(data)} 条记录")

    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()