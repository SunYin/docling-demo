# 多阶段构建 - 预下载模型
FROM python:3.11-slim as model-builder

# 设置工作目录
WORKDIR /app

# 安装 Docling 和依赖
RUN pip install --no-cache-dir docling

# 设置模型缓存目录
ENV DOCLING_CACHE_DIR=/models

# 复制模型下载脚本
COPY download_models.py .

# 预下载所有模型（这一步会比较耗时，但只在构建镜像时执行一次）
RUN python download_models.py

# 最终运行镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装 Docling（运行时需要）
RUN pip install --no-cache-dir docling

# 从构建阶段复制预下载的模型
ENV DOCLING_CACHE_DIR=/models
COPY --from=model-builder /models /models

# 复制应用代码
COPY quickstart.py .

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 默认命令
CMD ["python", "quickstart.py"]

