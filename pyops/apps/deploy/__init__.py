from flask import Blueprint

# 创建蓝图
deploy_bp = Blueprint('deploy', __name__)

# 导入视图
try:
    from . import views
except ImportError:
    pass