# 使用Ubuntu 20.04作为基础镜像
FROM ubuntu:20.04

# 避免安装过程中出现交互式提示
ARG DEBIAN_FRONTEND=noninteractive

# 安装Python 3.8和pip
RUN apt-get update && \
    apt-get install -y python3.8 python3-pip && \
    ln -s /usr/bin/python3.8 /usr/bin/python

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到容器中的/app
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 使用PyInstaller打包应用
RUN pip install pyinstaller
RUN pyinstaller --onefile ShuSDDNS.py

# CMD 命令可以设定为运行你的程序，也可以留空
CMD ["./dist/ShuSDDNS"]
