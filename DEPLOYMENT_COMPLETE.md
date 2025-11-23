# ✅ Qwen VLM PDF 提取方案 - 部署完成！

## 🎉 恭喜！所有文件已成功创建

### 📦 新增文件清单

#### 核心功能文件
1. ✅ `qwen_pdf_extractor.py` - Qwen VLM PDF 提取器（完整实现）
2. ✅ `process_resume.py` - 简历处理专用脚本
3. ✅ `quickstart_hybrid.py` - 智能混合方案（Docling + Qwen）

#### 配置文件
4. ✅ `requirements.txt` - Python 依赖（包含 dashscope、PyMuPDF等）
5. ✅ `.env.example` - 环境变量配置模板
6. ✅ `.gitignore` - Git 忽略文件（包含 .env、PDF 文件等）

#### 文档文件
7. ✅ `QWEN_GUIDE.md` - Qwen VLM 详细使用指南
8. ✅ `README.md` - 已更新，添加 Qwen VLM 方案说明

#### 依赖安装
9. ✅ 所有 Python 依赖已安装完成
   - dashscope (Qwen API 客户端)
   - PyMuPDF (PDF 处理)
   - Pillow (图片处理)
   - python-dotenv (环境变量管理)

---

## 🚀 立即开始使用

### 第一步：配置 API Key

```bash
# 1. 获取 API Key
# 访问: https://dashscope.console.aliyun.com/apiKey
# 注册并获取 API Key（格式：sk-xxxxxxxxx）

# 2. 创建配置文件
cp .env.example .env

# 3. 编辑 .env 文件，填入你的 API Key
# nano .env 或使用任何文本编辑器
# 将 DASHSCOPE_API_KEY=your_api_key_here 改为实际的 key
```

### 第二步：处理您的简历 PDF

```bash
# 运行简历处理脚本
python process_resume.py /Users/sunyin/Desktop/潘易_Android_简历.pdf

# 会自动生成: 潘易_Android_简历_提取.md
```

**预期输出**:
```
🚀 开始处理 PDF: 潘易_Android_简历.pdf
⚙️  配置: 模型=qwen-vl-max, DPI=300

📄 正在转换 PDF: /Users/sunyin/Desktop/潘易_Android_简历.pdf
  - 转换第 1/1 页...
✅ 共转换 1 页

📖 处理第 1/1 页...
✅ 第 1 页提取完成 (xxx 字符)

✅ PDF 处理完成！总字符数: xxx
💾 已保存到: 潘易_Android_简历_提取.md

================================================================================
✅ 处理完成！
📄 输出文件: 潘易_Android_简历_提取.md
================================================================================
```

---

## 📋 三种使用方式

### 方式 1: 简历处理（推荐）

```bash
python process_resume.py <PDF路径>
```

特点：
- ✅ 专门针对简历优化
- ✅ 自动提取个人信息、工作经历、技能等
- ✅ 输出结构化 Markdown

### 方式 2: 通用 PDF 处理

```bash
# 基础用法
python qwen_pdf_extractor.py document.pdf -o output.md

# 使用快速模型（省钱）
python qwen_pdf_extractor.py document.pdf --model qwen-vl-plus --dpi 200
```

特点：
- ✅ 适用于各种类型的 PDF
- ✅ 可自定义 DPI、模型等参数
- ✅ 支持命令行直接使用

### 方式 3: 智能混合方案

```bash
python quickstart_hybrid.py
```

特点：
- ✅ 优先使用免费的 Docling
- ✅ 失败自动切换 Qwen VLM
- ✅ 成本最优

---

## 💰 费用参考

| 场景 | 模型 | 页数 | 预估费用 |
|------|------|------|----------|
| 1页简历 | qwen-vl-max | 1 页 | ¥0.01-0.02 |
| 5页报告 | qwen-vl-max | 5 页 | ¥0.05-0.10 |
| 10页论文 | qwen-vl-plus | 10 页 | ¥0.04-0.08 |

**新用户福利**：阿里云通常提供免费额度，足够处理几百页！

---

## 🎯 方案对比总结

| 方案 | 成本 | 速度 | 精度 | 适用场景 |
|------|------|------|------|----------|
| **Docling** | 免费 | 快 | 良好 | 普通 PDF（有文字层） |
| **Qwen VLM** | 付费 | 中等 | 优秀 | 扫描件、受保护PDF、简历 |
| **混合方案** | 智能 | 自适应 | 最佳 | 自动选择最优方案 |

---

## 📚 相关文档

1. **快速使用**：查看 `README.md` 的"处理受保护 PDF"章节
2. **详细指南**：查看 `QWEN_GUIDE.md`
3. **代码示例**：查看 `quickstart_hybrid.py`

---

## 🔍 故障排查

### 问题 1: "请设置 DASHSCOPE_API_KEY 环境变量"

**原因**：API Key 未配置

**解决**：
```bash
# 方式 1: 使用 .env 文件
cp .env.example .env
# 编辑 .env，填入 API Key

# 方式 2: 直接设置环境变量
export DASHSCOPE_API_KEY="sk-your-key-here"
```

### 问题 2: "API 调用失败"

**可能原因**：
1. API Key 无效
2. 余额不足
3. 网络问题

**解决**：
- 检查 API Key 是否正确
- 访问 https://dashscope.console.aliyun.com/ 查看余额
- 检查网络连接

### 问题 3: 提取内容不准确

**解决**：
```bash
# 使用更精确的模型
python qwen_pdf_extractor.py document.pdf --model qwen-vl-max

# 提高图片分辨率
python qwen_pdf_extractor.py document.pdf --dpi 400
```

### 问题 4: 处理速度太慢

**解决**：
```bash
# 降低分辨率
python qwen_pdf_extractor.py document.pdf --dpi 200

# 使用更快的模型
python qwen_pdf_extractor.py document.pdf --model qwen-vl-plus
```

---

## 🧪 测试命令

### 验证环境

```bash
# 检查依赖是否安装
python -c "import dashscope; import fitz; from PIL import Image; print('✅ 环境正常')"

# 检查 API Key 配置
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key:', 'sk-***' if os.getenv('DASHSCOPE_API_KEY') else '未配置')"
```

### 快速测试

```bash
# 使用在线 PDF 测试（免费）
python quickstart.py

# 测试 Qwen VLM（需要 API Key）
python -c "from qwen_pdf_extractor import QwenPDFExtractor; print('✅ Qwen VLM 模块正常')"
```

---

## 📊 项目完整性检查

✅ 核心功能文件 (3个)
✅ 配置文件 (3个)  
✅ 文档文件 (2个)
✅ 依赖安装完成
✅ README 更新完成

**总计**: 8 个新文件 + 依赖安装 + 文档更新

---

## 🎓 进阶使用

### 批量处理

```python
from pathlib import Path
from qwen_pdf_extractor import QwenPDFExtractor

extractor = QwenPDFExtractor()

for pdf_file in Path("/path/to/pdfs").glob("*.pdf"):
    print(f"处理: {pdf_file.name}")
    content = extractor.extract_pdf(str(pdf_file))
    extractor.save_to_file(content, f"{pdf_file.stem}_output.md")
```

### 自定义提示词

```python
from qwen_pdf_extractor import QwenPDFExtractor

extractor = QwenPDFExtractor()

custom_prompt = """
请提取文档中的以下信息：
1. 标题和章节
2. 表格数据
3. 重要数字和日期

用 Markdown 格式输出。
"""

content = extractor.extract_pdf("document.pdf", prompt=custom_prompt)
print(content)
```

---

## 🆘 获取帮助

1. **查看帮助文档**
   ```bash
   python qwen_pdf_extractor.py --help
   python process_resume.py --help
   ```

2. **查看详细指南**
   - 阅读 `QWEN_GUIDE.md`
   - 阅读 `README.md`

3. **在线资源**
   - [Qwen VLM 官方文档](https://help.aliyun.com/zh/dashscope/developer-reference/tongyi-qianwen-vl-plus-api)
   - [DashScope 控制台](https://dashscope.console.aliyun.com/)

---

## 🎉 下一步

1. **配置 API Key** - 从阿里云获取
2. **运行简历处理** - 测试您的 PDF
3. **根据需求调整** - 选择合适的模型和参数
4. **集成到项目** - 在代码中使用 `QwenPDFExtractor`

---

## 📝 总结

您现在拥有一个完整的 PDF 处理解决方案：

- ✅ **免费方案**：Docling（适合普通 PDF）
- ✅ **付费方案**：Qwen VLM（适合复杂/受保护 PDF）
- ✅ **智能方案**：自动选择最优方案
- ✅ **容器化方案**：Docker/K8s 生产部署

**开始使用吧！** 🚀

