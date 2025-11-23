# 🚀 Qwen VLM - 快速参考

## ⚡ 一分钟快速开始

```bash
# 1. 配置 API Key
cp .env.example .env
# 编辑 .env，填入: DASHSCOPE_API_KEY=sk-xxx

# 2. 处理 PDF
python process_resume.py your_resume.pdf

# 3. 查看结果
cat your_resume_提取.md
```

## 📋 三个命令

| 命令 | 用途 | 成本 |
|------|------|------|
| `python process_resume.py file.pdf` | 简历处理 | ¥0.01/页 |
| `python qwen_pdf_extractor.py file.pdf -o out.md` | 通用处理 | ¥0.01/页 |
| `python quickstart_hybrid.py` | 智能方案 | 按需 |

## 🎯 常用参数

```bash
# 使用快速模型（省钱）
--model qwen-vl-plus

# 使用精确模型（推荐）
--model qwen-vl-max

# 降低分辨率（加速）
--dpi 200

# 提高分辨率（更准确）
--dpi 400

# 指定输出文件
-o output.md
```

## 💰 费用速查

- **1 页**: ¥0.01-0.02
- **5 页**: ¥0.05-0.10
- **10 页**: ¥0.04-0.08 (用 plus 模型)

## 🔧 故障速查

| 问题 | 解决方法 |
|------|----------|
| API Key 错误 | 检查 .env 文件 |
| 余额不足 | 访问控制台充值 |
| 提取不准确 | 用 `--model qwen-vl-max --dpi 400` |
| 速度太慢 | 用 `--model qwen-vl-plus --dpi 200` |

## 📚 快速链接

- 获取 API Key: https://dashscope.console.aliyun.com/apiKey
- 详细文档: 查看 QWEN_GUIDE.md
- 项目主页: 查看 README.md

## 🆘 获取帮助

```bash
python qwen_pdf_extractor.py --help
python process_resume.py --help
./start.sh  # 交互式启动
```

