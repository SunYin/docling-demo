#!/bin/bash
# Qwen VLM PDF 提取器 - 快速启动脚本

echo "🚀 Qwen VLM PDF 提取器 - 快速启动"
echo ""

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件"
    echo "📝 正在创建..."
    cp .env.example .env
    echo ""
    echo "✅ .env 文件已创建"
    echo "📌 请编辑 .env 文件，填入你的 DASHSCOPE_API_KEY"
    echo ""
    echo "获取 API Key: https://dashscope.console.aliyun.com/apiKey"
    echo ""
    exit 1
fi

# 检查 API Key
source .env
if [ -z "$DASHSCOPE_API_KEY" ] || [ "$DASHSCOPE_API_KEY" = "your_api_key_here" ]; then
    echo "❌ DASHSCOPE_API_KEY 未配置"
    echo "📝 请编辑 .env 文件，填入你的 API Key"
    echo ""
    echo "获取 API Key: https://dashscope.console.aliyun.com/apiKey"
    exit 1
fi

echo "✅ API Key 已配置: sk-***${DASHSCOPE_API_KEY: -8}"
echo ""

# 检查 Python 依赖
echo "🔍 检查 Python 依赖..."
if ! python -c "import dashscope, fitz, PIL, dotenv" 2>/dev/null; then
    echo "❌ 依赖未安装"
    echo "📦 正在安装..."
    pip install -r requirements.txt
    echo ""
fi

echo "✅ 依赖检查完成"
echo ""

# 显示使用方法
echo "========================================="
echo "📖 使用方法"
echo "========================================="
echo ""
echo "方式 1: 处理简历（推荐）"
echo "  python process_resume.py <PDF路径>"
echo ""
echo "方式 2: 通用 PDF 处理"
echo "  python qwen_pdf_extractor.py <PDF路径> -o output.md"
echo ""
echo "方式 3: 智能混合方案"
echo "  python quickstart_hybrid.py"
echo ""
echo "========================================="
echo ""

# 询问是否立即处理文件
read -p "是否要立即处理 PDF 文件？(y/n): " choice
if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
    read -p "请输入 PDF 文件路径: " pdf_path

    if [ -f "$pdf_path" ]; then
        echo ""
        echo "🚀 开始处理: $pdf_path"
        echo ""
        python process_resume.py "$pdf_path"
    else
        echo "❌ 文件不存在: $pdf_path"
    fi
fi

echo ""
echo "✅ 完成！"

