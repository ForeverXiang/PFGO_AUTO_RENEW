# 使用官方Python ARM64镜像
FROM arm64v8/python:3.8

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到容器中的/app
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 使用PyInstaller打包应用
RUN pyinstaller --onefile your_script_name.py

# 指定生成的可执行文件的位置，方便后续步骤中提取
CMD ["cp", "/app/dist/ShuSDDNS", "/path/to/dist/ShuSDDNS"]
