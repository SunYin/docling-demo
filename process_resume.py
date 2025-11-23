"""
专门处理简历 PDF 的脚本
使用 Qwen VLM API 提取受保护或扫描简历的内容
"""
from qwen_pdf_extractor import QwenPDFExtractor
from pathlib import Path
import sys


def main():
    # 简历路径（请根据实际情况修改）
    resume_path = "/Users/sunyin/Desktop/潘易_Android_简历.pdf"

    if not Path(resume_path).exists():
        print(f"❌ 文件不存在: {resume_path}")
        print("\n💡 使用方法:")
        print("1. 修改脚本中的 resume_path 变量")
        print("2. 或者作为命令行参数传入:")
        print(f"   python process_resume.py <PDF文件路径>")

        if len(sys.argv) > 1:
            resume_path = sys.argv[1]
            if not Path(resume_path).exists():
                print(f"\n❌ 指定的文件不存在: {resume_path}")
                sys.exit(1)
        else:
            sys.exit(1)

    print("🚀 开始处理简历 PDF...")
    print(f"📄 文件: {resume_path}")

    # 创建提取器
    try:
        extractor = QwenPDFExtractor()
    except ValueError as e:
        print(f"\n❌ 初始化失败: {e}")
        print("\n💡 请先配置 API Key:")
        print("1. 创建 .env 文件")
        print("2. 添加: DASHSCOPE_API_KEY=your_api_key_here")
        print("3. 或者设置环境变量: export DASHSCOPE_API_KEY=xxx")
        print("\n获取 API Key: https://dashscope.console.aliyun.com/apiKey")
        sys.exit(1)

    # 自定义简历提取提示词
    resume_prompt = """请提取这份简历中的所有信息，并按照以下格式整理输出：

# 个人信息
- 姓名：
- 联系方式：
- 邮箱：
- 其他联系方式：

# 教育背景

# 工作经历

# 项目经验

# 技能

# 其他

请保持原文内容，不要遗漏任何信息。用 Markdown 格式输出。"""

    # 提取内容
    try:
        content = extractor.extract_pdf(
            resume_path,
            output_format='markdown',
            dpi=300,
            prompt=resume_prompt
        )

        # 保存结果
        output_file = Path(resume_path).stem + "_提取.md"
        extractor.save_to_file(content, output_file)

        print("\n" + "="*80)
        print("✅ 处理完成！")
        print(f"📄 输出文件: {output_file}")
        print("="*80)

        # 显示预览
        print("\n内容预览:")
        print("-" * 80)
        preview_len = min(1000, len(content))
        print(content[:preview_len])
        if len(content) > preview_len:
            print("...")
            print(f"\n(还有 {len(content) - preview_len} 字符，完整内容请查看输出文件)")

    except Exception as e:
        print(f"\n❌ 处理失败: {e}")
        print("\n请检查:")
        print("1. DASHSCOPE_API_KEY 环境变量是否正确设置")
        print("2. API Key 是否有效且有足够余额")
        print("3. 网络连接是否正常")
        print("4. PDF 文件是否损坏")
        sys.exit(1)


if __name__ == "__main__":
    main()

