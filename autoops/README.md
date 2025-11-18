# AutoOps 自动化运维平台

## 项目简介
AutoOps 是一个面向初学者的自动化运维平台，支持主机管理、批量命令执行、日志面板等功能，覆盖主流运维开发技术栈，适合练习和扩展。

## 主要功能
- 主机资产管理（录入、分组、批量导入）
- 批量命令执行，结果收集
- 任务历史与日志归档
- Web管理界面（Flask）
- 配置管理与定时任务（可扩展）

## 技术栈
- Python 3.7+
- Flask + Bootstrap + Flask-SQLAlchemy
- paramiko（SSH）
- APScheduler（定时任务）
- requests、python-dotenv、PyMySQL

## 目录结构
```
autoops/
├── config/           # 配置与环境变量
├── core/             # 业务逻辑（主机、任务、SSH等）
├── database/         # ORM模型与数据库管理
├── scripts/          # 启动、初始化等脚本
├── utils/            # 工具类
├── web/              # Web界面
│   └── templates/    # 前端模板
├── tests/            # 单元测试
├── requirements.txt  # 依赖
└── README.md         # 项目说明
```

## 安装与部署
1. 安装依赖：`pip install -r requirements.txt`
2. 配置数据库和环境变量，参考 config/.env.example
3. 初始化数据库：`python scripts/init_db.py`
4. 启动平台：`python scripts/start_web.py`
5. 访问 Web 界面：`http://localhost:5000`

## 学习要点
- 多主机批量运维的设计与实现
- SSH自动化、任务调度、Web开发、ORM
- 日志、配置管理
- 代码结构与可维护性

---
如需详细开发文档和代码注释，请参考各模块源码。
