from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from celery import Celery
from config import config
import os

# 初始化数据库
db = SQLAlchemy()
# 初始化SocketIO
socketio = SocketIO()

def create_app(config_name=None):
    import os
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    socketio.init_app(app)
    
    # 注册蓝图
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from apps.host import host_bp
    from apps.deploy import deploy_bp
    from apps.monitor import monitor_bp
    from apps.schedule import schedule_bp
    from apps.account import account_bp
    from apps.terminal import terminal_bp
    
    app.register_blueprint(host_bp, url_prefix='/host')
    app.register_blueprint(deploy_bp, url_prefix='/deploy')
    app.register_blueprint(monitor_bp, url_prefix='/monitor')
    app.register_blueprint(schedule_bp, url_prefix='/schedule')
    app.register_blueprint(account_bp, url_prefix='/account')
    app.register_blueprint(terminal_bp, url_prefix='/terminal')
    
    # 首页路由
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app

# def create_celery(app=None):
#     app = app or create_app()
#     celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
#     celery.conf.update(app.config)
#     return celery