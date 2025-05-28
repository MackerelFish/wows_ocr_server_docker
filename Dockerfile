# 使用 Python 3.10 作为基础镜像
FROM python:3.10.17-slim-bookworm
# 更新包列表并安装 libGL.so.1
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*
# 升级 pip
RUN pip install --upgrade pip
# 设置工作目录
WORKDIR /wows_ocr
# 复制当前目录的内容到容器的工作目录
COPY ./ /wows_ocr
# 安装依赖
RUN pip install -r requirement.txt
# 安装 PaddlePaddle
RUN pip install paddlepaddle==2.6.2 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
# 指定容器启动时执行的命令
CMD ["python", "main.py"]

