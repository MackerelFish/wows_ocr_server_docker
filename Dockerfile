# 使用 Python 3.8 作为基础镜像
FROM python:3.8
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
RUN pip install paddlepaddle==2.6.1 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
# 指定容器启动时执行的命令
CMD ["python", "main.py"]

