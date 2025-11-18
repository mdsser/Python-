from flask import request, jsonify
from . import account_bp
from app import db
from datetime import datetime

# 模拟用户数据
@account_bp.route('', methods=['GET'])
def get_accounts():
    # 这里应该从数据库获取实际用户数据
    accounts = [
        {
            'id': 1,
            'username': 'admin',
            'email': 'admin@example.com',
            'role': 'admin',
            'status': 'active',
            'created_at': '2025-08-01 10:00:00'
        },
        {
            'id': 2,
            'username': 'user1',
            'email': 'user1@example.com',
            'role': 'user',
            'status': 'active',
            'created_at': '2025-08-02 14:30:00'
        }
    ]
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': accounts
    })

@account_bp.route('/profile', methods=['GET'])
def get_profile():
    # 这里应该从数据库获取当前用户信息
    profile = {
        'id': 1,
        'username': 'admin',
        'email': 'admin@example.com',
        'role': 'admin',
        'created_at': '2025-08-01 10:00:00'
    }
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': profile
    })

@account_bp.route('/change-password', methods=['POST'])
def change_password():
    data = request.json
    required_fields = ['old_password', 'new_password']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'code': 1, 'message': '参数错误'}), 400
    
    # 这里应该实现修改密码的逻辑
    return jsonify({
        'code': 0,
        'message': '密码修改成功'
    })