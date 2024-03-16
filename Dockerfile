# 使用官方Python ARM64镜像
FROM arm64v8/python:3.8

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到容器中的/app
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 使用PyInstaller打包应用
RUN pyinstaller --onefile ShuSDDNS.py

# CMD 命令在这里不需要或者可以设定为运行你的程序
CMD ["./dist/ShuSDDNS"]
