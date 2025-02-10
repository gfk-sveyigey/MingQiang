# 二开推荐阅读[如何提高项目构建效率](https://developers.weixin.qq.com/miniprogram/dev/wxcloudrun/src/scene/build/speed.html)
# 选择基础镜像。如需更换，请到[dockerhub官方仓库](https://hub.docker.com/_/python?tab=tags)自行选择后替换。
# 已知alpine镜像与pytorch有兼容性问题会导致构建失败，如需使用pytorch请务必按需更换基础镜像。
# 更换为3.20版本，以使用较新的三方库
FROM alpine:3.20

# 容器默认时区为UTC，如需使用上海时间请启用以下时区设置命令
# RUN apk add tzdata && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo Asia/Shanghai > /etc/timezone

# 使用 HTTPS 协议访问容器云调用证书安装
RUN apk add ca-certificates

# 安装构建工具和依赖库，以使用Flask-APScheduler库
RUN apk update && apk add build-base libffi-dev

# 安装依赖包，如需其他依赖包，请到alpine依赖包管理(https://pkgs.alpinelinux.org/packages?name=php8*imagick*&branch=v3.20)查找。
# 选用国内镜像源以提高下载速度
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tencent.com/g' /etc/apk/repositories \
# 安装python3
# && apk add --update --no-cache python3 py3-pip \
# 安装python3,包管理库及虚拟环境库
&& apk add --update --no-cache python3 py3-pip py3-virtualenv\
&& rm -rf /var/cache/apk/*

# 拷贝当前项目到/app目录下（.dockerignore中文件除外）
COPY . /app

# 设定当前的工作目录
WORKDIR /app

# # 安装依赖到指定的/install文件夹
# # 选用国内镜像源以提高下载速度
# RUN pip config set global.index-url http://mirrors.cloud.tencent.com/pypi/simple \
# && pip config set global.trusted-host mirrors.cloud.tencent.com \
# && pip install --upgrade pip \
# # pip install scipy 等数学包失败，可使用 apk add py3-scipy 进行， 参考安装 https://pkgs.alpinelinux.org/packages?name=py3-scipy&branch=v3.20
# && pip install --user -r requirements.txt

# 创建虚拟环境,创建至工作目录会被自动删除文件。
RUN python3 -m venv /opt/venv

# # 调试：列出虚拟环境的目录内容
# RUN ls -la venv/bin/
# RUN ls -la venv/

# 激活虚拟环境并安装依赖
RUN . /opt/venv/bin/activate \
    && pip install --upgrade pip \
    && pip config set global.index-url http://mirrors.cloud.tencent.com/pypi/simple \
    && pip config set global.trusted-host mirrors.cloud.tencent.com \
    && pip install -r requirements.txt

# 暴露端口。
# 此处端口必须与「服务设置」-「流水线」以及「手动上传代码包」部署时填写的端口一致，否则会部署失败。
EXPOSE 80

# 执行启动命令
# 写多行独立的CMD命令是错误写法！只有最后一行CMD命令会被执行，之前的都会被忽略，导致业务报错。
# 请参考[Docker官方文档之CMD命令](https://docs.docker.com/engine/reference/builder/#cmd)
# CMD ["python3", "run.py", "0.0.0.0", "80"]

# 激活虚拟环境
CMD ["/opt/venv/bin/python", "run.py", "0.0.0.0", "80"]
