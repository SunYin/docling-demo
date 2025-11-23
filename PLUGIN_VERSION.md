# Docling Qwen OCR 插件版本

## 🎯 核心区别

### ❌ 旧版本（docling_qwen_pipeline.py）
```
Docling 处理 PDF
  ↓ 失败
Qwen VL 独立重新处理 PDF  ← 完全独立，不是管线的一部分
```

### ✅ 新版本（docling_qwen_integrated.py + qwen_ocr_plugin.py）
```
Docling 管线
  ├─ PDF 解析
  ├─ 布局分析
  ├─ 表格识别
  ├─ OCR 引擎 ← Qwen VL 作为 OCR 引擎集成在这里！
  └─ 导出 Markdown
```

---

## 📁 文件说明

### 1. `qwen_ocr_plugin.py` - Qwen OCR 插件
实现 Docling 的 `BaseOcrModel` 接口，可以作为 OCR 引擎集成到管线中。

**关键特性**：
- ✅ 继承 `BaseOcrModel`
- ✅ 实现 `__call__` 方法（Docling 管线调用接口）
- ✅ 接收 Page 对象，返回带 OCR 结果的 Page
- ✅ 保留文档结构（表格、布局等）

### 2. `docling_qwen_integrated.py` - 集成版主程序
使用 Qwen OCR 插件创建完整的 Docling 管线。

**关键特性**：
- ✅ Qwen 作为管线的一部分运行
- ✅ 保留 Docling 的文档结构分析能力
- ✅ 支持表格识别、布局分析等高级特性
- ✅ 统一的处理流程

---

## 🚀 使用方法

### 安装依赖

```bash
pip install docling dashscope pymupdf pillow python-dotenv
```

### 配置 API Key

```bash
# 方法 1: 环境变量
export DASHSCOPE_API_KEY="your-api-key"

# 方法 2: .env 文件
echo "DASHSCOPE_API_KEY=your-api-key" > .env
```

### 运行示例

#### 1. 处理普通 PDF
```bash
python docling_qwen_integrated.py document.pdf
```

#### 2. 处理受保护/扫描 PDF
```bash
python docling_qwen_integrated.py 潘易_Android_简历.pdf --force-ocr
```

#### 3. 处理在线 PDF
```bash
python docling_qwen_integrated.py "https://arxiv.org/pdf/2408.09869" --preview-only
```

#### 4. 自定义输出
```bash
python docling_qwen_integrated.py document.pdf -o output.md
```

---

## 🔍 技术实现

### BaseOcrModel 接口

```python
class QwenOcrModel(BaseOcrModel):
    """实现 Docling OCR 接口"""
    
    def __call__(
        self, 
        conv_res: ConversionResult, 
        page_batch: Iterable[Page]
    ) -> Iterable[Page]:
        """
        Docling 管线会调用这个方法处理每个页面
        """
        for page in page_batch:
            # 1. 从 page.image 获取页面图片
            # 2. 调用 Qwen VL API 进行 OCR
            # 3. 将结果添加到 page.ocr_cells
            # 4. 返回处理后的 page
            yield processed_page
```

### 集成到管线

```python
# 创建 Qwen OCR 实例
qwen_ocr = QwenOcrModel(api_key="xxx")

# Docling 管线会自动调用
pipeline_options = PdfPipelineOptions(
    do_ocr=True,  # 启用 OCR
    generate_page_images=True,  # 生成页面图片
)

converter = DocumentConverter(...)

# 转换时，Docling 内部会调用 qwen_ocr(result, pages)
result = converter.convert("document.pdf")
```

---

## 📊 对比表

| 特性 | 旧版本（后备方案） | 新版本（插件集成） |
|------|------------------|------------------|
| **架构** | Docling → 失败 → Qwen | Docling(内含 Qwen OCR) |
| **文档结构** | ❌ 丢失 | ✅ 完整保留 |
| **表格识别** | ❌ 丢失 | ✅ 保留 |
| **布局分析** | ❌ 丢失 | ✅ 保留 |
| **处理流程** | 两次处理 | 一次处理 |
| **效率** | 低（重复处理） | 高（统一管线） |
| **扩展性** | ❌ 难以扩展 | ✅ 标准插件接口 |

---

## 🎯 优势

### 1. 保留文档结构
```markdown
# Docling 分析的标题
- 项目列表
  - 子项目

| 表格 | 数据 |
|------|------|
| Qwen | OCR  |  ← 表格结构保留！
```

### 2. 统一管线
```python
# 一次调用完成所有处理
result = converter.convert("document.pdf")
markdown = result.document.export_to_markdown()
```

### 3. 标准接口
```python
# 可以轻松切换其他 OCR 引擎
class MyCustomOCR(BaseOcrModel):
    def __call__(self, conv_res, page_batch):
        # 实现自定义 OCR
        pass
```

---

## ⚠️ 注意事项

### Qwen VL API 限制

Qwen VL API **不返回文字坐标信息**，所以：

```python
# 我们创建一个覆盖整页的 OCR 结果
ocr_cell = OcrCell(
    text="全部识别的文字",
    bbox=BoundingBox(l=0, t=0, r=page_width, b=page_height)
)
```

这意味着：
- ✅ 可以提取文字内容
- ✅ 可以保留 Docling 分析的布局
- ⚠️ 但 OCR 文字没有精确的位置信息

### 建议使用场景

1. **受保护 PDF** → ✅ 使用 Qwen 插件版
2. **扫描 PDF** → ✅ 使用 Qwen 插件版
3. **图片 PDF** → ✅ 使用 Qwen 插件版
4. **普通 PDF** → 可选，Docling 标准 OCR 也很好

---

## 🧪 测试

```bash
# 1. 测试插件加载
python -c "from qwen_ocr_plugin import QwenOcrModel; print('✅ 插件加载成功')"

# 2. 测试基础功能
export DASHSCOPE_API_KEY="your-key"
python docling_qwen_integrated.py "https://arxiv.org/pdf/2408.09869" --preview-only

# 3. 测试 OCR 功能
python docling_qwen_integrated.py your_pdf.pdf --force-ocr
```

---

## 📚 扩展阅读

- Docling 文档: https://docling-project.github.io/docling/
- Qwen VL: https://github.com/QwenLM/Qwen-VL
- DashScope API: https://dashscope.console.aliyun.com/

---

## 🎉 总结

**现在 Qwen VL 是真正作为 Docling 管线的一部分运行！**

- ✅ 实现了 `BaseOcrModel` 接口
- ✅ 集成到 Docling 处理管线
- ✅ 保留文档结构和布局
- ✅ 统一的处理流程

这才是真正的"管线集成"！🚀

