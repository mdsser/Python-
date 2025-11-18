import pandas as pd
import json
import psycopg2
from math import sqrt

# 快速绑定无重复项
# ========== 配置 ==========
CAMERA_XLSX = "监控设备.xlsx"
FIRE_XLSX = "消防设备.xlsx"

DB_CONFIG = {
    'host': '130.10.2.251',                    # 主机地址
    'port': 5434,                              # 主机端口
    'dbname': 'postgres',                      # 数据库名
    'user': 'postgres',                        # 数据库用户
    'password': 'qwer963.'                     # 数据库密码
}

START_ID = 1985245409940513188                  # 插入数据的起始地址

# 将消防点位映射为具体设备描述
LAST_TO_EXPLAIN = {
    '1': '消防烟感报警',
    '2': '消防手动报警器',
    '3': '消防喇叭',
    '4': '消防栓'
}

# ========== 辅助函数 ==========
def safe_parse_tag(tag_str):
    if pd.isna(tag_str) or tag_str == '{}' or not tag_str.strip():
        return {}
    try:
        return json.loads(tag_str)
    except:
        return {}

def extract_point(val):
    if pd.isna(val):
        return 0.0
    try:
        return float(str(val).replace('px', '').strip())
    except:
        return 0.0

# ========== 主逻辑 ==========
def main():
    # 1. 读取摄像头
    cam_df = pd.read_excel(CAMERA_XLSX, dtype=str)
    cameras = []
    for _, row in cam_df.iterrows():
        tag = safe_parse_tag(row['tag'])
        buildNamePath = tag.get('buildNamePath', '')
        x = extract_point(tag.get('pointX'))
        y = extract_point(tag.get('pointY'))
        cameras.append({
            'device_id': row['device_id'],
            'device_name': row['device_name'],
            'buildNamePath': buildNamePath,
            'x': x,
            'y': y
        })

    # 2. 读取消防设备
    fire_df = pd.read_excel(FIRE_XLSX, dtype=str)
    fire_devices = []
    for _, row in fire_df.iterrows():
        tag = safe_parse_tag(row['tag'])
        buildNamePath = tag.get('buildNamePath', '')
        x = extract_point(tag.get('pointX'))
        y = extract_point(tag.get('pointY'))
        last = str(row['last']) if pd.notna(row['last']) else '99'
        fire_devices.append({
            'device_id': row['device_id'],
            'device_name': row['device_name'],
            'buildNamePath': buildNamePath,
            'x': x,
            'y': y,
            'last': last
        })

    print(f"✅ 加载 {len(cameras)} 个摄像头，{len(fire_devices)} 个消防设备")

    # 3. 按 buildNamePath 分组
    cam_groups = {}
    fire_groups = {}
    for cam in cameras:
        key = cam['buildNamePath']
        cam_groups.setdefault(key, []).append(cam)
    for fire in fire_devices:
        key = fire['buildNamePath']
        fire_groups.setdefault(key, []).append(fire)

    # 4. 连接数据库
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # 5. 查询已存在的绑定对（去重用）
    cur.execute('SELECT device_id, bind_device_id FROM "public"."iot_d_bind_device_info";')
    existing_pairs = set(cur.fetchall())
    print(f"✅ 数据库中已有 {len(existing_pairs)} 条绑定记录")

    current_id = START_ID
    inserted = 0

    # 6. 绑定并插入（仅新数据）
    for buildNamePath in set(cam_groups.keys()) & set(fire_groups.keys()):
        for cam in cam_groups[buildNamePath]:
            for fire in fire_groups[buildNamePath]:
                # 去重检查（注意顺序：device_id=消防, bind_device_id=摄像头）
                pair = (fire['device_id'], cam['device_id'])
                if pair in existing_pairs:
                    continue

                # 距离检查
                dx = cam['x'] - fire['x']
                dy = cam['y'] - fire['y']
                dist = sqrt(dx*dx + dy*dy)
                if dist > 130.0:
                    continue

                bind_identifier = cam['device_name']
                bind_explain = LAST_TO_EXPLAIN.get(fire['last'], '其他消防设备')

                # 插入
                cur.execute("""
                    INSERT INTO "public"."iot_d_bind_device_info"
                    ("id", "device_id", "bind_device_id", "bind_identifier", "bind_explain")
                    VALUES (%s, %s, %s, %s, %s)
                """, (current_id, fire['device_id'], cam['device_id'], bind_identifier, bind_explain))

                current_id += 1
                inserted += 1
                existing_pairs.add(pair)  # 防止同一批重复

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ 新增绑定记录：{inserted} 条")


if __name__ == "__main__":
    main()