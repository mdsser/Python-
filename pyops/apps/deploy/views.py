from flask import request, jsonify
from . import deploy_bp
from .models import Deploy, DeployHistory
from app import db
from datetime import datetime
from apps.host.models import Host
import time

# celery = create_celery()

# @celery.task
def deploy_task(deploy_id, user_id):
    deploy = Deploy.query.get(deploy_id)
    if not deploy:
        return
    
    history = DeployHistory(
        deploy_id=deploy_id,
        start_time=datetime.utcnow(),
        status='running',
        created_by=user_id
    )
    db.session.add(history)
    db.session.commit()
    
    logs = []
    try:
        # 获取主机列表
        host_ids = [int(hid) for hid in deploy.host_ids.split(',')]
        hosts = Host.query.filter(Host.id.in_(host_ids)).all()
        
        for host in hosts:
            logs.append(f'开始部署到主机: {host.name}({host.hostname})')
            # 这里应该实现实际的部署逻辑
            # 1. 克隆代码
            # 2. 切换分支
            # 3. 执行预部署脚本
            # 4. 部署代码到目标路径
            # 5. 执行后部署脚本
            time.sleep(2)  # 模拟部署过程
            logs.append(f'成功部署到主机: {host.name}({host.hostname})')
        
        history.status = 'success'
        deploy.status = 'success'
    except Exception as e:
        logs.append(f'部署失败: {str(e)}')
        history.status = 'failed'
        deploy.status = 'failed'
    
    history.end_time = datetime.utcnow()
    history.logs = '\n'.join(logs)
    db.session.commit()

@deploy_bp.route('', methods=['GET'])
def get_deploys():
    deploys = Deploy.query.all()
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': [{
            'id': deploy.id,
            'name': deploy.name,
            'repository': deploy.repository,
            'branch': deploy.branch,
            'status': deploy.status,
            'created_at': deploy.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for deploy in deploys]
    })

@deploy_bp.route('/<int:deploy_id>', methods=['GET'])
def get_deploy(deploy_id):
    deploy = Deploy.query.get_or_404(deploy_id)
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {
            'id': deploy.id,
            'name': deploy.name,
            'repository': deploy.repository,
            'branch': deploy.branch,
            'deploy_path': deploy.deploy_path,
            'pre_deploy_script': deploy.pre_deploy_script,
            'post_deploy_script': deploy.post_deploy_script,
            'host_ids': deploy.host_ids,
            'status': deploy.status,
            'created_at': deploy.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@deploy_bp.route('', methods=['POST'])
def create_deploy():
    data = request.json
    required_fields = ['name', 'repository', 'deploy_path', 'host_ids']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'code': 1, 'message': '参数错误'}), 400
    
    if Deploy.query.filter_by(name=data['name']).first():
        return jsonify({'code': 1, 'message': '部署名称已存在'}), 400
    
    deploy = Deploy(
        name=data['name'],
        repository=data['repository'],
        branch=data.get('branch', 'master'),
        deploy_path=data['deploy_path'],
        pre_deploy_script=data.get('pre_deploy_script', ''),
        post_deploy_script=data.get('post_deploy_script', ''),
        host_ids=data['host_ids'],
        created_by=1  # 假设用户ID为1
    )
    db.session.add(deploy)
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '创建成功',
        'data': {'id': deploy.id, 'name': deploy.name}
    })

@deploy_bp.route('/<int:deploy_id>/deploy', methods=['POST'])
def run_deploy(deploy_id):
    deploy = Deploy.query.get_or_404(deploy_id)
    deploy.status = 'running'
    db.session.commit()
    
    # 异步执行部署任务
    deploy_task(deploy_id, 1)  # 同步执行部署任务，假设用户ID为1
    
    return jsonify({
        'code': 0,
        'message': '部署任务已启动',
        'data': {'deploy_id': deploy_id}
    })

@deploy_bp.route('/<int:deploy_id>/history', methods=['GET'])
def get_deploy_history(deploy_id):
    histories = DeployHistory.query.filter_by(deploy_id=deploy_id).order_by(DeployHistory.created_at.desc()).all()
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': [{
            'id': history.id,
            'start_time': history.start_time.strftime('%Y-%m-%d %H:%M:%S') if history.start_time else '',
            'end_time': history.end_time.strftime('%Y-%m-%d %H:%M:%S') if history.end_time else '',
            'status': history.status,
            'commit_id': history.commit_id
        } for history in histories]
    })

@deploy_bp.route('/history/<int:history_id>/logs', methods=['GET'])
def get_history_logs(history_id):
    history = DeployHistory.query.get_or_404(history_id)
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {
            'logs': history.logs
        }
    })