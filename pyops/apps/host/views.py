from flask import request, jsonify
from . import host_bp
from .models import Host, HostGroup
from app import db
import paramiko
import time

@host_bp.route('/groups', methods=['GET'])
def get_groups():
    groups = HostGroup.query.all()
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': [{
            'id': group.id,
            'name': group.name,
            'description': group.description,
            'created_at': group.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for group in groups]
    })

@host_bp.route('/groups', methods=['POST'])
def create_group():
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'code': 1, 'message': '参数错误'}), 400
    
    if HostGroup.query.filter_by(name=data['name']).first():
        return jsonify({'code': 1, 'message': '分组名称已存在'}), 400
    
    group = HostGroup(
        name=data['name'],
        description=data.get('description', '')
    )
    db.session.add(group)
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '创建成功',
        'data': {'id': group.id, 'name': group.name}
    })

@host_bp.route('', methods=['GET'])
def get_hosts():
    group_id = request.args.get('group_id')
    if group_id:
        hosts = Host.query.filter_by(group_id=group_id).all()
    else:
        hosts = Host.query.all()
    
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': [host.to_dict() for host in hosts]
    })

@host_bp.route('/<int:host_id>', methods=['GET'])
def get_host(host_id):
    host = Host.query.get_or_404(host_id)
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': host.to_dict()
    })

@host_bp.route('', methods=['POST'])
def create_host():
    data = request.json
    required_fields = ['name', 'hostname', 'username']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'code': 1, 'message': '参数错误'}), 400
    
    if Host.query.filter_by(name=data['name']).first():
        return jsonify({'code': 1, 'message': '主机名称已存在'}), 400
    
    host = Host(
        name=data['name'],
        hostname=data['hostname'],
        port=data.get('port', 22),
        username=data['username'],
        password=data.get('password'),
        key_file=data.get('key_file'),
        passphrase=data.get('passphrase'),
        group_id=data.get('group_id'),
        description=data.get('description', '')
    )
    db.session.add(host)
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '创建成功',
        'data': host.to_dict()
    })

@host_bp.route('/<int:host_id>', methods=['PUT'])
def update_host(host_id):
    host = Host.query.get_or_404(host_id)
    data = request.json
    # 在这里添加更新主机的逻辑
    # 为了简化，我们先留空
    return jsonify({'code': 0, 'message': '更新成功', 'data': host.to_dict()})

@host_bp.route('/<int:host_id>', methods=['DELETE'])
def delete_host(host_id):
    host = Host.query.get_or_404(host_id)
    db.session.delete(host)
    db.session.commit()
    return jsonify({'code': 0, 'message': '删除成功'})

@host_bp.route('/<int:host_id>/terminal', methods=['GET'])
def terminal(host_id):
    host = Host.query.get_or_404(host_id)
    return jsonify({'code': 0, 'message': 'success', 'data': host.to_dict()})
    
    if 'name' in data and data['name'] != host.name:
        if Host.query.filter_by(name=data['name']).first():
            return jsonify({'code': 1, 'message': '主机名称已存在'}), 400
        host.name = data['name']
    
    host.hostname = data.get('hostname', host.hostname)
    host.port = data.get('port', host.port)
    host.username = data.get('username', host.username)
    host.password = data.get('password', host.password)
    host.key_file = data.get('key_file', host.key_file)
    host.passphrase = data.get('passphrase', host.passphrase)
    host.group_id = data.get('group_id', host.group_id)
    host.description = data.get('description', host.description)
    
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '更新成功',
        'data': host.to_dict()
    })

@host_bp.route('/<int:host_id>', methods=['DELETE'])
def delete_host(host_id):
    host = Host.query.get_or_404(host_id)
    db.session.delete(host)
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '删除成功'
    })

@host_bp.route('/<int:host_id>/test', methods=['GET'])
def test_host_connection(host_id):
    host = Host.query.get_or_404(host_id)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        if host.key_file:
            key = paramiko.RSAKey.from_private_key_file(host.key_file, password=host.passphrase)
            ssh.connect(host.hostname, port=host.port, username=host.username, pkey=key, timeout=5)
        else:
            ssh.connect(host.hostname, port=host.port, username=host.username, password=host.password, timeout=5)
        
        ssh.close()
        host.status = 'online'
        db.session.commit()
        return jsonify({
            'code': 0,
            'message': '连接成功'
        })
    except Exception as e:
        host.status = 'offline'
        db.session.commit()
        return jsonify({
            'code': 1,
            'message': f'连接失败: {str(e)}'
        }), 500