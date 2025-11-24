#!/usr/bin/env python3
"""
Docling 集成 Qwen VL OCR 插件版本

真正将 Qwen VL 作为 Docling 管线的 OCR 引擎
"""
import os
import sys
import argparse
from pathlib import Path
from typing import Optional

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, OcrOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.models.factories import get_ocr_factory

# 导入自定义 Qwen OCR 插件
from qwen_ocr_plugin import QwenOcrModel, QwenOcrOptions


def register_qwen_ocr():
    """注册 Qwen OCR 引擎到 Docling"""
    try:
        # 获取全局 OCR 工厂实例 (使用默认 allow_external_plugins=False)
        # 注意：必须使用 get_ocr_factory 获取单例，否则 StandardPdfPipeline 会创建新实例
        ocr_factory = get_ocr_factory(allow_external_plugins=False)

        # 检查是否已注册
        if hasattr(ocr_factory, '_classes'):
            print("✓ 使用手动注册 Qwen OCR 引擎")
            # 直接添加到工厂的类字典中
            ocr_factory._classes[QwenOcrOptions] = QwenOcrModel

        return True
    except Exception as e:
        print(f"⚠️  注册 Qwen OCR 引擎失败: {e}")
        return False


def create_qwen_pipeline(
    ocr_enabled: bool = True,
    force_ocr: bool = False,
    api_key: Optional[str] = None,
    model: str = "qwen-vl-plus"
) -> DocumentConverter:
    """
    创建使用 Qwen VL OCR 的 Docling 管线

    Args:
        ocr_enabled: 是否启用 OCR
        force_ocr: 是否强制 OCR 所有页面
        api_key: Qwen API Key
        model: Qwen 模型名称

    Returns:
        配置好的 DocumentConverter
    """
    # 先注册 Qwen OCR 到工厂
    register_qwen_ocr()

    # 配置 OCR 选项 - 使用 QwenOcrOptions
    ocr_options = QwenOcrOptions(
        lang=["en", "zh"],  # 支持英文和中文
        force_full_page_ocr=force_ocr,
        model_name=model
    ) if ocr_enabled else None

    # 配置 PDF 管线
    pipeline_options = PdfPipelineOptions(
        do_ocr=ocr_enabled,
        do_table_structure=True,
        ocr_options=ocr_options,
        images_scale=2.0,
        generate_page_images=True,  # 生成页面图片供 OCR 使用
        generate_picture_images=True,
    )

    # 创建转换器
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
                backend=PyPdfiumDocumentBackend,
            )
        }
    )

    print("✓ Qwen VL OCR 已集成到 Docling 管线")
    return converter


def main():
    parser = argparse.ArgumentParser(
        description="Docling with Qwen VL OCR Plugin (Integrated Pipeline)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 基础用法（自动使用 Qwen OCR）
  python docling_qwen_integrated.py document.pdf
  
  # 指定 API Key
  export DASHSCOPE_API_KEY="your-api-key"
  python docling_qwen_integrated.py document.pdf
  
  # 强制 OCR 所有页面
  python docling_qwen_integrated.py document.pdf --force-ocr
  
  # 处理在线 PDF
  python docling_qwen_integrated.py "https://arxiv.org/pdf/2408.09869"
  
  # 禁用 OCR（仅文本提取）
  python docling_qwen_integrated.py document.pdf --no-ocr

环境变量:
  DASHSCOPE_API_KEY    阿里云 DashScope API Key
  QWEN_MODEL          Qwen 模型名称 (默认: qwen-vl-plus)
        """
    )

    parser.add_argument("pdf", help="PDF 文件路径或 URL")
    parser.add_argument("--output", "-o", help="输出 Markdown 文件路径")
    parser.add_argument("--force-ocr", action="store_true", help="强制 OCR 所有页面")
    parser.add_argument("--no-ocr", action="store_true", help="禁用 OCR")
    parser.add_argument("--model", default="qwen-vl-plus", help="Qwen 模型名称")
    parser.add_argument("--preview-only", action="store_true", help="仅预览不保存")

    args = parser.parse_args()

    try:
        # 检查 API Key
        api_key = os.getenv('DASHSCOPE_API_KEY')
        if not args.no_ocr and not api_key:
            print("❌ 错误: 未找到 DASHSCOPE_API_KEY")
            print()
            print("请设置 API Key:")
            print("  export DASHSCOPE_API_KEY='your-api-key'")
            print()
            print("或者使用 --no-ocr 禁用 OCR")
            print()
            print("获取 API Key: https://dashscope.console.aliyun.com/apiKey")
            sys.exit(1)

        print("=" * 80)
        print(f"📄 处理 PDF: {args.pdf}")
        print("=" * 80)

        # 创建 Qwen OCR 管线
        converter = create_qwen_pipeline(
            ocr_enabled=not args.no_ocr,
            force_ocr=args.force_ocr,
            api_key=api_key,
            model=args.model
        )

        # 转换文档
        print(f"\n🔄 开始转换...")
        result = converter.convert(args.pdf)

        # 导出 Markdown
        markdown_content = result.document.export_to_markdown()

        print(f"\n✅ 转换完成! 提取了 {len(markdown_content)} 字符")

        # 显示预览
        print("\n" + "=" * 80)
        print("📝 内容预览 (前 500 字符):")
        print("=" * 80)
        preview = markdown_content[:500] + "..." if len(markdown_content) > 500 else markdown_content
        print(preview)
        print("=" * 80)

        # 保存文件
        if not args.preview_only:
            if args.output:
                output_path = Path(args.output)
            else:
                pdf_name = Path(args.pdf).stem if not args.pdf.startswith('http') else "output"
                output_path = Path(f"{pdf_name}_qwen_output.md")

            output_path.write_text(markdown_content, encoding='utf-8')
            print(f"\n💾 已保存到: {output_path.absolute()}")
        else:
            print("\n💡 预览模式: 文件未保存")

    except Exception as e:
        print(f"\n❌ 错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
