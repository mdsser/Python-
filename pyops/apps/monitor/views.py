from flask import request, jsonify
from . import monitor_bp
from app import db
from datetime import datetime

# 模拟监控数据
@monitor_bp.route('/data', methods=['GET'])
def get_monitor_data():
    # 这里应该从数据库或监控系统获取实际数据
    data = {
        'cpu_usage': 65.2,
        'memory_usage': 78.5,
        'disk_usage': 45.3,
        'network_in': 12345,
        'network_out': 6789,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': data
    })

@monitor_bp.route('/metrics', methods=['GET'])
def get_metrics():
    # 这里应该返回所有可监控的指标
    metrics = [
        {'id': 1, 'name': 'CPU使用率', 'unit': '%', 'description': '服务器CPU使用率'},
        {'id': 2, 'name': '内存使用率', 'unit': '%', 'description': '服务器内存使用率'},
        {'id': 3, 'name': '磁盘使用率', 'unit': '%', 'description': '服务器磁盘使用率'},
        {'id': 4, 'name': '网络流入', 'unit': 'B/s', 'description': '服务器网络流入速率'},
        {'id': 5, 'name': '网络流出', 'unit': 'B/s', 'description': '服务器网络流出速率'}
    ]
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': metrics
    })