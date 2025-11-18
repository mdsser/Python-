import pandas as pd
import json
import psycopg2
from math import sqrt

# ========== 配置 ==========
CAMERA_XLSX = "监控设备.xlsx"
FIRE_XLSX = "消防设备.xlsx"

DB_CONFIG = {
    'host': '192.168.1.12',                 # 定义主机地址
    'port': 5432,                           # 端口号
    'dbname': 'jlkj_iot_platform_dev',      # 数据库名称
    'user': 'postgres',                     # 用户名
    'password': 'qwer963.'                  # 数据库密码
}

START_ID = 1985245409940512789              # 起始ID号

# 类型映射
LAST_TO_EXPLAIN = {
    '1': '消防烟感报警',
    '2': '消防手动报警器',
    '3': '消防喇叭',
    '4': '消防栓'
}

# ========== 辅助函数 ==========
# 解析JSON字段
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
        buildNamePath = tag.get('buildNamePath', f"{row.get('building_name', '')}-{row.get('floor_name', '')}")

        #  取到坐标值，x和y
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
        buildNamePath = tag.get('buildNamePath', '未知')
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

    # 3. 按 buildNamePath 分组（精确到楼栋+楼层）
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

    current_id = START_ID
    inserted = 0

    # 5. 绑定并插入（仅在相同 buildNamePath 内）
    for buildNamePath in set(cam_groups.keys()) & set(fire_groups.keys()):
        for cam in cam_groups[buildNamePath]:
            for fire in fire_groups[buildNamePath]:
                dx = cam['x'] - fire['x']
                dy = cam['y'] - fire['y']
                dist = sqrt(dx*dx + dy*dy)
                if dist <= 125.0:
                    bind_identifier = cam['device_name']  # 直接用摄像头的 device_name
                    bind_explain = LAST_TO_EXPLAIN.get(fire['last'], '其他消防设备')
                    cur.execute("""
                        INSERT INTO "public"."iot_d_bind_device_info"
                        ("id", "device_id", "bind_device_id", "bind_identifier", "bind_explain")
                        VALUES (%s, %s, %s, %s, %s)
                    """, (current_id, fire['device_id'], cam['device_id'], bind_identifier, bind_explain))
                    current_id += 1
                    inserted += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ 绑定完成！共插入 {inserted} 条记录")

if __name__ == "__main__":
    main()