# 创建应用实例
import sys

from mingqiang import app

# 启动Flask Web服务
if __name__ == '__main__':
    app.run(host=sys.argv[1], port=sys.argv[2])
    # app.run(host="0.0.0.0", port=56948)
