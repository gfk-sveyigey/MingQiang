import os

# 是否开启debug模式
DEBUG = False

# 读取数据库环境变量
username = os.environ.get("MYSQL_USERNAME", 'mingqiang')
password = os.environ.get("MYSQL_PASSWORD", 'Lgq984512!')
db_address = os.environ.get("MYSQL_ADDRESS", '10.39.100.18:3306')

