from flask import Blueprint

# 创建蓝图
host_bp = Blueprint('host', __name__)

# 导入视图
try:
    from . import views
except ImportError:
    pass