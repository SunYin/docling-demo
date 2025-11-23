# Qwen VLM PDF 提取器快速使用指南

## 🎯 适用场景

当遇到以下情况时，使用 Qwen VLM 方案：
- ✅ PDF 无法用 Docling 提取文字（受保护、加密）
- ✅ 扫描件 PDF（图片格式）
- ✅ 简历类文档（通常格式复杂）
- ✅ 需要高精度识别中文内容

## 📋 准备工作

### 1. 获取 API Key

访问阿里云 DashScope 控制台：
https://dashscope.console.aliyun.com/apiKey

注册并获取 API Key（格式：`sk-xxxxxxxxxxxxxxxxxx`）

### 2. 配置 API Key

**方式 1: 使用 .env 文件（推荐）**

```bash
# 创建 .env 文件
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
# DASHSCOPE_API_KEY=sk-your-api-key-here
```

**方式 2: 使用环境变量**

```bash
# macOS/Linux
export DASHSCOPE_API_KEY="sk-your-api-key-here"

# Windows
set DASHSCOPE_API_KEY=sk-your-api-key-here
```

## 🚀 使用方法

### 方式 1: 处理简历（推荐）

```bash
# 直接运行（会处理 /Users/sunyin/Desktop/潘易_Android_简历.pdf）
python process_resume.py

# 或者指定文件路径
python process_resume.py /path/to/your/resume.pdf
```

**输出**：会生成 `xxx_提取.md` 文件，包含提取的简历内容。

### 方式 2: 通用 PDF 提取

```bash
# 基础用法
python qwen_pdf_extractor.py /path/to/your.pdf

# 保存到文件
python qwen_pdf_extractor.py /path/to/your.pdf -o output.md

# 使用更快的模型（降低成本）
python qwen_pdf_extractor.py /path/to/your.pdf --model qwen-vl-plus

# 调整图片分辨率（默认 300 DPI）
python qwen_pdf_extractor.py /path/to/your.pdf --dpi 200
```

### 方式 3: 混合方案（智能选择）

```bash
# 优先使用免费的 Docling，失败自动切换 Qwen
python quickstart_hybrid.py
```

这个脚本会：
1. 先尝试用 Docling 提取（免费）
2. 如果失败，自动切换到 Qwen VLM（收费）

## 💻 在代码中使用

```python
from qwen_pdf_extractor import QwenPDFExtractor

# 创建提取器
extractor = QwenPDFExtractor()

# 提取 PDF
content = extractor.extract_pdf(
    pdf_path="/path/to/your.pdf",
    output_format='markdown',
    dpi=300
)

# 打印结果
print(content)

# 保存到文件
extractor.save_to_file(content, "output.md")
```

### 自定义提示词

```python
# 自定义提取格式
custom_prompt = """
请提取这份文档中的所有信息，重点关注：
1. 标题和章节结构
2. 表格数据
3. 数字和日期

用 Markdown 格式输出。
"""

content = extractor.extract_pdf(
    pdf_path="document.pdf",
    prompt=custom_prompt
)
```

## 💰 费用说明

| 模型 | 价格（每千 tokens） | 速度 | 精度 | 推荐场景 |
|------|---------------------|------|------|----------|
| `qwen-vl-plus` | ¥0.008 | 快 | 良好 | 批量处理、成本敏感 |
| `qwen-vl-max` | ¥0.02 | 慢 | 最佳 | 重要文档、高精度要求 |

**估算示例**：
- 1 页简历约 500-1000 tokens
- 使用 `qwen-vl-max` 处理 1 页 ≈ ¥0.01-0.02
- 处理 10 页文档 ≈ ¥0.1-0.2

## ⚙️ 配置选项

在 `.env` 文件中配置：

```bash
# 使用的模型
QWEN_MODEL=qwen-vl-max  # 或 qwen-vl-plus

# 最大 tokens（默认 4096）
QWEN_MAX_TOKENS=4096

# 温度参数（0-1，越低越稳定）
QWEN_TEMPERATURE=0.1
```

## 🔍 常见问题

### Q: 提示 "请设置 DASHSCOPE_API_KEY 环境变量"？
A: 说明 API Key 没有配置。请按照上面的"准备工作"配置。

### Q: API 调用失败，提示余额不足？
A: 访问 https://dashscope.console.aliyun.com/ 充值。新用户通常有免费额度。

### Q: 处理速度很慢？
A: 
- 降低 DPI：`--dpi 200`（默认 300）
- 使用更快的模型：`--model qwen-vl-plus`
- Qwen VLM 需要网络请求，比本地 Docling 慢是正常的

### Q: 提取的内容不准确？
A: 
- 使用 `qwen-vl-max` 模型（更准确）
- 提高 DPI：`--dpi 400`
- 使用自定义提示词明确要求

### Q: 能处理多语言文档吗？
A: 可以！Qwen VLM 支持中英日韩等多种语言。

## 📊 效果对比

| 方案 | 成本 | 速度 | 精度 | 适用场景 |
|------|------|------|------|----------|
| **Docling** | 免费 | 快（首次慢） | 良好 | 普通 PDF、有文字层 |
| **Qwen VLM** | 收费 | 中等 | 优秀 | 扫描件、受保护 PDF |
| **混合方案** | 按需 | 智能 | 最佳 | 自动选择最优方案 |

## 🎓 进阶用法

### 批量处理

```python
from pathlib import Path
from qwen_pdf_extractor import QwenPDFExtractor

extractor = QwenPDFExtractor()

# 处理目录下所有 PDF
pdf_dir = Path("/path/to/pdfs")
for pdf_file in pdf_dir.glob("*.pdf"):
    print(f"处理: {pdf_file.name}")
    content = extractor.extract_pdf(str(pdf_file))
    
    # 保存结果
    output_file = pdf_file.stem + "_output.md"
    extractor.save_to_file(content, output_file)
```

### 错误处理

```python
try:
    content = extractor.extract_pdf("document.pdf")
except ValueError as e:
    print(f"配置错误: {e}")
except Exception as e:
    print(f"处理失败: {e}")
    # 可以尝试降低 DPI 或更换模型
```

## 🆘 获取帮助

```bash
# 查看命令行帮助
python qwen_pdf_extractor.py --help
python process_resume.py --help
```

## 📚 相关文档

- [Qwen VLM 官方文档](https://help.aliyun.com/zh/dashscope/developer-reference/tongyi-qianwen-vl-plus-api)
- [DashScope API 文档](https://help.aliyun.com/zh/dashscope/)
- [定价说明](https://help.aliyun.com/zh/dashscope/developer-reference/tongyi-thousand-questions-metering-and-billing)

