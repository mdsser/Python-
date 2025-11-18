from datetime import datetime
from app import db

class Deploy(db.Model):
    __tablename__ = 'deploys'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    repository = db.Column(db.String(255), nullable=False)
    branch = db.Column(db.String(100), default='master')
    deploy_path = db.Column(db.String(255), nullable=False)
    pre_deploy_script = db.Column(db.Text)
    post_deploy_script = db.Column(db.Text)
    host_ids = db.Column(db.Text, nullable=False)  # 用逗号分隔的主机ID
    status = db.Column(db.String(20), default='pending')  # pending, running, success, failed
    created_by = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DeployHistory(db.Model):
    __tablename__ = 'deploy_histories'
    id = db.Column(db.Integer, primary_key=True)
    deploy_id = db.Column(db.Integer, db.ForeignKey('deploys.id'), nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20))  # success, failed
    commit_id = db.Column(db.String(100))
    logs = db.Column(db.Text)
    created_by = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)