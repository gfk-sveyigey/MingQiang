from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
import config

__all__ = [
    "app",
    "scheduler",
    "db",
    "house_id_generator",
    "user_id_generator",
]

# 因MySQLDB不支持Python3，使用pymysql扩展库代替MySQLDB库
pymysql.install_as_MySQLdb()

# 初始化web应用
app = Flask(__name__, instance_relative_config=True)
app.config['DEBUG'] = config.DEBUG

# 设定数据库链接
if app.config["DEBUG"]:
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{config.username}:{config.password}@{config.db_address}/Test'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{config.username}:{config.password}@{config.db_address}/MiniProgram'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800
# app.config['SQLALCHEMY_ECHO'] = True  # debug

# 初始化DB操作对象
db = SQLAlchemy(app, session_options={"expire_on_commit":False})

# 加载数据库模型
from mingqiang import model

# 创建库表
with app.app_context():
    # db.drop_all()
    db.create_all()  # 创建表

# 加载雪花id生成器
from mingqiang.snowflake import house_id_generator, user_id_generator



# 实例化定时任务
from flask_apscheduler import APScheduler
# 禁用调度器 API
app.config['SCHEDULER_API_ENABLED'] = False
scheduler = APScheduler()
scheduler.init_app(app)
# 启动调度器
scheduler.start()

# 导入地图服务
from mingqiang.services import map
from mingqiang import jobs


# # 启动服务
# import run

# 加载控制器
from mingqiang import views

# 加载配置
app.config.from_object('config')
