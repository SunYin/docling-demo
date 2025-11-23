"""
混合方案：优先使用 Docling，失败时使用 Qwen VLM
智能选择最合适的 PDF 处理方式
"""
from docling.document_converter import DocumentConverter
from qwen_pdf_extractor import QwenPDFExtractor
import os
from pathlib import Path


def extract_pdf_smart(pdf_path: str, force_qwen: bool = False) -> str:
    """
    智能提取 PDF 内容

    Args:
        pdf_path: PDF 文件路径
        force_qwen: 强制使用 Qwen VLM

    Returns:
        提取的 Markdown 内容
    """
    pdf_name = Path(pdf_path).name if not pdf_path.startswith('http') else pdf_path

    if not force_qwen:
        # 方案 1: 尝试使用 Docling（免费）
        print(f"🔄 尝试使用 Docling 处理: {pdf_name}")
        try:
            converter = DocumentConverter()
            doc = converter.convert(pdf_path).document
            content = doc.export_to_markdown()

            # 检查是否成功提取内容（简单判断）
            if len(content.strip()) > 100:  # 至少有一些内容
                print("✅ Docling 提取成功!")
                return content
            else:
                print("⚠️  Docling 提取内容过少，切换到 Qwen VLM...")
                raise ValueError("Content too short")

        except Exception as e:
            print(f"⚠️  Docling 处理失败: {e}")
            print("🔄 切换到 Qwen VLM 方案...")

    # 方案 2: 使用 Qwen VLM（需要 API Key）
    print(f"🤖 使用 Qwen VLM 处理: {pdf_name}")
    try:
        extractor = QwenPDFExtractor()
        content = extractor.extract_pdf(pdf_path)
        print("✅ Qwen VLM 提取成功!")
        return content
    except Exception as e:
        print(f"❌ Qwen VLM 处理失败: {e}")
        raise


def main():
    # 测试文件
    test_files = [
        "https://arxiv.org/pdf/2408.09869",  # 在线 PDF（Docling 可处理）
        "/Users/sunyin/Desktop/潘易_Android_简历.pdf",  # 本地受保护 PDF
    ]

    for source in test_files:
        print("\n" + "="*80)
        print(f"处理文件: {source}")
        print("="*80)

        # 检查本地文件是否存在
        if not source.startswith('http') and not Path(source).exists():
            print(f"⚠️  文件不存在，跳过: {source}")
            continue

        try:
            # 对于简历类 PDF，直接使用 Qwen（更准确）
            force_qwen = "简历" in source or "resume" in source.lower()
            content = extract_pdf_smart(source, force_qwen=force_qwen)

            # 输出前 500 字符预览
            print("\n📄 内容预览:")
            print("-" * 80)
            preview = content[:500] + "..." if len(content) > 500 else content
            print(preview)

            # 保存到文件
            if source.startswith('http'):
                output_file = "online_pdf_output.md"
            else:
                output_file = f"{Path(source).stem}_output.md"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n💾 完整内容已保存到: {output_file}")

        except Exception as e:
            print(f"\n❌ 处理失败: {e}")


if __name__ == "__main__":
    main()

