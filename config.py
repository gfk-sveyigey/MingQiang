import os

# 版本
version = "1.1.2"

# 是否开启debug模式
DEBUG = False

# 读取数据库环境变量
username = os.environ.get("MYSQL_USERNAME", 'mingqiang')
password = os.environ.get("MYSQL_PASSWORD", 'Lgq984512!')
db_address = os.environ.get("MYSQL_ADDRESS", 'sh-cynosdbmysql-grp-3rogqg0s.sql.tencentcdb.com:24358')
map_key = os.environ.get("MAP_KEY", "FIOBZ-KUB65-BFRIO-IREHG-E7LI5-46FHK")
map_SK = os.environ.get("MAP_SK", "FcRQzl9KwP7kP8lbkPNw6iUyGh11zQ3U")

