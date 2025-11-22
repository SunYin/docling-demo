# Docling Demo

这是一个使用 [Docling](https://github.com/DS4SD/docling) 的演示项目。

Docling 是一个强大的文档处理工具，旨在简化文档解析和转换工作，特别适合用于生成式 AI (Gen AI) 和 RAG (检索增强生成) 应用。它可以将 PDF、Word、Excel、HTML 等多种格式转换为统一的结构化数据。

## ✨ 主要特性

*   **多格式支持**：支持 PDF, DOCX, PPTX, XLSX, HTML, 图片, 音频等多种格式。
*   **高级 PDF 理解**：能够识别页面布局、阅读顺序、表格结构、代码块和数学公式。
*   **统一数据模型**：将所有文档转换为统一的 `DoclingDocument` 对象。
*   **多种导出选项**：支持导出为 Markdown, JSON, HTML 等。
*   **OCR 集成**：内置支持 EasyOCR, Tesseract 等引擎处理扫描件。

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

## 📚 更多资源

*   [Docling 官方文档](https://ds4sd.github.io/docling/)
*   [GitHub 仓库](https://github.com/DS4SD/docling)
