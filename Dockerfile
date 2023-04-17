# 指定要使用的基础镜像
FROM python:alpine

LABEL version="1.0"
LABEL description="test-platform"

# 设置环境变量
ENV FLASK_APP app.py
ENV FLASK_ENV test
ENV FLASK_RUN_PORT 80
ENV FLASK_RUN_HOST 0.0.0.0

# 设置工作目录
WORKDIR /home/flask

# 将应用程序源代码拷贝到工作目录
COPY . .

# 安装依赖
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories && \
    apk update && \
    apk add --no-cache build-base && \
    apk add --no-cache gcc musl-dev linux-headers openssl-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del build-base &&  \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    rm -rf /var/cache/apk/*


EXPOSE 80

# 设置容器启动命令
CMD ["flask", "run"]