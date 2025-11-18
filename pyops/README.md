# PyOps 运维管理平台

PyOps是一个基于Python和Flask构建的轻量化运维管理平台，参考了Spug项目的设计理念，旨在提供简单、易用的服务器管理和应用部署功能。

## 功能特点

- 主机管理：支持主机分组、SSH连接管理
- 应用部署：支持多主机并行部署、部署历史记录
- 监控中心：服务器资源监控
- 任务计划：定时任务管理
- 账号管理：用户权限控制

## 技术栈

- 后端：Python, Flask, Flask-SQLAlchemy, Celery
- 数据库：MySQL, Redis
- 前端：Bootstrap, Chart.js, Socket.IO

## 环境准备

1. 安装Python 3.8+
2. 安装MySQL 5.7+
3. 安装Redis 5.0+

## 配置方法

1. 克隆项目到本地

```bash
cd d:\python代码
# 项目已创建，无需克隆
```

2. 创建虚拟环境

```bash
python -m venv venv
# Windows激活虚拟环境
venv\Scripts\activate
# Linux/Mac激活虚拟环境
source venv/bin/activate
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 配置数据库

编辑`config.py`文件，修改数据库连接信息：

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost/pyops'
```

5. 初始化数据库

```bash
# 后续会添加数据库迁移脚本
```

## 运行项目

1. 启动Redis服务

```bash
redis-server
```

2. 启动Celery worker

```bash
celery -A app.celery worker --loglevel=info
```

3. 启动Flask应用

```bash
# 设置环境变量
set FLASK_APP=app.py
set FLASK_ENV=development
# 运行应用
flask run --host=0.0.0.0 --port=5000
```

4. 访问应用

打开浏览器，访问 http://localhost:5000

## 项目结构

```
pyops/
├── apps/                 # 功能模块
│   ├── host/             # 主机管理
│   ├── deploy/           # 应用部署
│   ├── monitor/          # 监控中心
│   └── ...
├── config.py             # 配置文件
├── app.py                # 主应用文件
├── requirements.txt      # 依赖文件
├── templates/            # 模板文件
│   └── index.html        # 首页模板
└── README.md             # 项目说明
```

## 扩展建议

1. 添加监控模块，实现服务器资源监控
2. 添加任务计划模块，支持定时任务
3. 完善用户权限管理
4. 添加日志收集和分析功能
5. 开发更多自动化运维工具