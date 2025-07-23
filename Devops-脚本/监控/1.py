# monitor.py
from flask import Flask, render_template
import psutil
import sqlite3
import threading
import time

app = Flask(__name__)
DB_FILE = 'monitor.db'


def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_FILE)
    conn.execute('''CREATE TABLE IF NOT EXISTS metrics (
                 id INTEGER PRIMARY KEY,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                 cpu REAL,
                 memory REAL,
                 disk REAL)''')
    conn.commit()
    conn.close()


def collect_metrics():
    """收集系统指标"""
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return cpu, mem, disk


def save_to_db(cpu, mem, disk):
    """保存数据到数据库"""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT INTO metrics (cpu, memory, disk) VALUES (?, ?, ?)",
                 (cpu, mem, disk))
    conn.commit()
    conn.close()


def collector_loop():
    """定时收集数据"""
    while True:
        cpu, mem, disk = collect_metrics()
        save_to_db(cpu, mem, disk)
        time.sleep(60)  # 每分钟收集一次


@app.route('/')
def dashboard():
    """监控仪表盘"""
    conn = sqlite3.connect(DB_FILE)

    # 获取最新数据
    current = conn.execute(
        "SELECT cpu, memory, disk FROM metrics ORDER BY timestamp DESC LIMIT 1"
    ).fetchone()

    # 获取历史数据（最近2小时）
    history = conn.execute(
        "SELECT timestamp, cpu, memory, disk FROM metrics "
        "WHERE timestamp > datetime('now', '-2 hours')"
    ).fetchall()

    conn.close()

    return render_template('dashboard.html',
                           current=current,
                           history=history)


def start_background_collector():
    """启动后台收集线程"""
    thread = threading.Thread(target=collector_loop)
    thread.daemon = True
    thread.start()


if __name__ == '__main__':
    init_db()
    start_background_collector()
    app.run(host='0.0.0.0', port=5000)