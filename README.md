# Docling Demo

这是一个使用 [Docling](https://github.com/DS4SD/docling) 的演示项目。

Docling 是一个强大的文档处理工具，旨在简化文档解析和转换工作，特别适合用于生成式 AI (Gen AI) 和 RAG (检索增强生成) 应用。它可以将 PDF、Word、Excel、HTML 等多种格式转换为统一的结构化数据。

## ✨ 主要特性

*   **多格式支持**：支持 PDF, DOCX, PPTX, XLSX, HTML, 图片, 音频等多种格式。
*   **高级 PDF 理解**：能够识别页面布局、阅读顺序、表格结构、代码块和数学公式。
*   **统一数据模型**：将所有文档转换为统一的 `DoclingDocument` 对象。
*   **多种导出选项**：支持导出为 Markdown, JSON, HTML 等。
*   **OCR 集成**：内置支持 EasyOCR, Tesseract 等引擎处理扫描件。

## 📁 项目结构

```
docling-demo/
├── quickstart.py           # 基础使用示例
├── download_models.py      # 预下载模型脚本
├── Dockerfile              # Docker 镜像构建文件（模型预打包）
├── docker-compose.yml      # Docker Compose 配置
├── .dockerignore          # Docker 构建忽略文件
├── k8s/                   # Kubernetes 部署配置
│   ├── deployment.yaml    # 应用部署配置
│   └── pvc.yaml          # 持久卷声明（共享模型存储）
└── README.md             # 本文档
```

## 🛠️ 安装指南

建议使用虚拟环境来运行此项目，以避免依赖冲突。

### 1. 创建并激活虚拟环境

**macOS / Linux:**
```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate
```

**Windows:**
```powershell
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
.venv\Scripts\activate
```

### 2. 安装 Docling

激活虚拟环境后，安装 `docling` 包：

```bash
pip install docling
```

如果需要 OCR 或其他高级功能支持，可以安装额外的依赖：

```bash
# 安装 EasyOCR 支持
pip install "docling[easyocr]"

# 安装视觉语言模型 (VLM) 支持
pip install "docling[vlm]"
```

## 🚀 快速开始

### Python 代码示例

创建一个名为 `main.py` 的文件，并运行以下代码将文档转换为 Markdown：

```python
from docling.document_converter import DocumentConverter

# 也可以是本地文件路径，例如 "./my_doc.pdf"
source = "https://arxiv.org/pdf/2408.09869" 

converter = DocumentConverter()
result = converter.convert(source)

# 导出为 Markdown
print(result.document.export_to_markdown())
```

### 命令行工具 (CLI)

Docling 也提供了命令行工具直接处理文件：

```bash
# 将 PDF 转换为 Markdown
docling https://arxiv.org/pdf/2206.01062
```

### ⚠️ 首次运行说明

**首次运行会比较慢（可能需要 5-15 分钟），这是正常现象！**

Docling 使用 AI 模型进行文档解析（布局识别、表格检测等），第一次运行时需要：
- 下载多个深度学习模型（总大小约 1-2GB）
- 模型会缓存到本地：`~/.cache/docling/`（macOS/Linux）或 `%USERPROFILE%\.cache\docling\`（Windows）

**后续运行会直接使用缓存的模型，速度会快很多！**

如果想提前下载模型，可以运行：
```bash
python download_models.py
```

## 🐳 容器化部署

为了解决首次启动慢的问题，生产环境建议使用 Docker/K8s 部署，将模型预打包到镜像中。

### 方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **镜像内置模型** | 启动快，无需外部依赖 | 镜像较大（3-5GB） | 单机部署、开发测试 |
| **外部卷挂载** | 镜像小，多容器共享模型 | 需要配置共享存储 | 生产环境、K8s 集群 |
| **NAS/NFS 挂载** | 统一管理，易于更新 | 依赖网络存储性能 | 大规模集群部署 |

### Docker 本地部署

#### 1. 构建镜像（模型预打包）

```bash
# 构建镜像（首次构建会下载模型，需要 5-15 分钟）
docker build -t docling-demo:latest .

# 查看镜像大小
docker images docling-demo
```

#### 2. 运行容器

```bash
# 使用镜像内置模型（推荐）
docker run --rm docling-demo:latest

# 或者挂载本地模型缓存目录（适合多次重建容器）
docker run --rm \
  -v ~/.cache/docling:/models \
  -e DOCLING_CACHE_DIR=/models \
  docling-demo:latest
```

### Docker Compose 部署

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

`docker-compose.yml` 已配置好两种方案，根据需求取消注释对应的挂载配置。

### Kubernetes 部署

#### 方案 1: 使用镜像内置模型（简单快速）

```bash
# 1. 构建并推送镜像到仓库
docker build -t your-registry/docling-demo:latest .
docker push your-registry/docling-demo:latest

# 2. 修改 k8s/deployment.yaml 中的镜像地址
# image: your-registry/docling-demo:latest

# 3. 注释掉 deployment.yaml 中的 volumeMounts 和 volumes 部分

# 4. 部署应用
kubectl apply -f k8s/deployment.yaml
```

#### 方案 2: 使用共享 PVC（生产推荐）

```bash
# 1. 创建 PVC 和初始化 Job（下载模型到共享存储）
kubectl apply -f k8s/pvc.yaml

# 2. 等待模型下载完成
kubectl wait --for=condition=complete job/docling-model-downloader --timeout=30m

# 3. 部署应用（使用共享模型）
kubectl apply -f k8s/deployment.yaml

# 4. 检查部署状态
kubectl get pods -l app=docling
kubectl logs -l app=docling
```

#### 方案 3: 使用 NFS/NAS 存储

1. 预先在 NAS 上下载模型：
```bash
# 在有网络的机器上运行
export DOCLING_CACHE_DIR=/mnt/nas/docling-models
python download_models.py
```

2. 修改 `k8s/deployment.yaml`，使用 NFS 卷：
```yaml
volumes:
- name: models
  nfs:
    server: your-nas-server.local
    path: /path/to/docling-models
    readOnly: true
```

3. 部署应用：
```bash
kubectl apply -f k8s/deployment.yaml
```

### 🔧 高级配置

#### 自定义模型缓存路径

```bash
# 设置环境变量
export DOCLING_CACHE_DIR=/custom/path/to/models

# 运行应用
python quickstart.py
```

#### 网络代理配置

如果下载模型需要代理：

```bash
# Docker
docker build --build-arg HTTP_PROXY=http://proxy:port \
             --build-arg HTTPS_PROXY=http://proxy:port \
             -t docling-demo:latest .

# 运行时
docker run -e HTTP_PROXY=http://proxy:port \
           -e HTTPS_PROXY=http://proxy:port \
           docling-demo:latest
```

#### 镜像优化

如果不需要 OCR 或 VLM 功能，可以修改 `Dockerfile`：
```dockerfile
# 只安装基础版本
RUN pip install --no-cache-dir docling

# 而不是
# RUN pip install --no-cache-dir "docling[easyocr,vlm]"
```

## 📚 更多资源

*   [Docling 官方文档](https://ds4sd.github.io/docling/)
*   [GitHub 仓库](https://github.com/DS4SD/docling)

## ❓ 常见问题

### Q1: 为什么首次运行这么慢？
A: Docling 使用深度学习模型进行文档解析，首次运行需要下载约 1-2GB 的模型文件。模型会缓存到本地，后续运行会快很多。

### Q2: 如何加速模型下载？
A: 如果在国内网络环境下载慢，可以：
- 使用代理：`export HTTP_PROXY=http://proxy:port`
- 使用已下载好的模型：将模型目录挂载到容器或复制到 `~/.cache/docling/`

### Q3: Docker 镜像太大怎么办？
A: 可以创建精简版镜像：
- 只安装基础 Docling（不含 OCR/VLM）：`pip install docling`
- 使用外部挂载的模型缓存，避免将模型打包进镜像
- 使用多阶段构建优化镜像层

### Q4: K8s 环境下如何实现多 Pod 共享模型？
A: 推荐使用方案 2 或方案 3：
- **方案 2**: 创建 ReadOnlyMany PVC，多个 Pod 共享
- **方案 3**: 使用 NFS/NAS 挂载，统一管理模型文件

### Q5: 模型存储在哪里？
A: 默认路径：
- Linux/macOS: `~/.cache/docling/`
- Windows: `%USERPROFILE%\.cache\docling\`
- 可通过 `DOCLING_CACHE_DIR` 环境变量自定义

### Q6: 生产环境推荐哪种部署方案？
A: 根据规模选择：
- **小规模（1-5 个容器）**: 使用镜像内置模型，简单可靠
- **中等规模（5-20 个容器）**: 使用 PVC 共享模型，节省存储
- **大规模（20+ 个容器）**: 使用 NFS/NAS，集中管理和更新

## 🎯 最佳实践

1. **开发环境**: 直接使用 Python 虚拟环境，首次运行后会缓存模型
2. **测试环境**: 使用 Docker 镜像（内置模型），确保环境一致性
3. **生产环境**: 使用 K8s + PVC/NFS，实现高可用和资源共享
4. **CI/CD**: 在构建阶段预下载模型，避免运行时下载失败
5. **监控**: 关注容器内存使用（建议 ≥2GB）和 CPU 负载

## 📝 License

本项目为演示项目，遵循 MIT License。Docling 库本身遵循 [MIT License](https://github.com/DS4SD/docling/blob/main/LICENSE)。

