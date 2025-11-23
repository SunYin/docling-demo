#!/usr/bin/env python3
"""
Docling 自定义管线：集成 Qwen VL 作为 OCR 后端
支持自定义 OCR 模型和配置 Docling 处理管线
"""
import os
import sys
import io
import argparse
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Docling imports
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, OcrOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend

# Qwen VL imports
try:
    import dashscope
    from dashscope import MultiModalConversation
    QWEN_AVAILABLE = True
except ImportError:
    QWEN_AVAILABLE = False
    print("⚠️  dashscope not installed. Install with: pip install dashscope", file=sys.stderr)

try:
    from PIL import Image
    import fitz  # PyMuPDF
    IMAGE_SUPPORT = True
except ImportError:
    IMAGE_SUPPORT = False

# Load environment variables
load_dotenv()


class QwenOCRBackend:
    """自定义 Qwen VL OCR 后端（用于替代 Docling 默认 OCR）"""

    def __init__(self, api_key: Optional[str] = None, model: str = "qwen-vl-max"):
        """
        初始化 Qwen OCR 后端

        Args:
            api_key: DashScope API Key
            model: Qwen VL 模型名称
        """
        if not QWEN_AVAILABLE:
            raise RuntimeError("dashscope library not available")

        self.api_key = api_key or os.getenv('DASHSCOPE_API_KEY')
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY not found in environment")

        dashscope.api_key = self.api_key
        self.model = model
        print(f"✓ Qwen VL OCR Backend initialized (model: {model})")

    def extract_text_from_image(self, image: Image.Image, prompt: Optional[str] = None) -> str:
        """
        使用 Qwen VL 从图片提取文本

        Args:
            image: PIL Image 对象
            prompt: 自定义提示词

        Returns:
            提取的文本
        """
        # Convert PIL Image to bytes
        buf = io.BytesIO()
        image.save(buf, format='PNG')
        buf.seek(0)

        # Save to temp file for Qwen API
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            tmp.write(buf.read())
            tmp_path = tmp.name

        try:
            # Default OCR prompt
            if prompt is None:
                prompt = "请识别图片中的所有文字内容，保持原有格式和布局。"

            messages = [{
                'role': 'user',
                'content': [
                    {'image': f'file://{tmp_path}'},
                    {'text': prompt}
                ]
            }]

            response = MultiModalConversation.call(
                model=self.model,
                messages=messages
            )

            if response.status_code == 200:
                return response.output.choices[0].message.content[0]['text']
            else:
                print(f"⚠️  Qwen API error: {response.message}", file=sys.stderr)
                return ""
        finally:
            # Clean up temp file
            os.unlink(tmp_path)


def create_docling_pipeline(use_qwen_ocr: bool = False,
                            ocr_enabled: bool = True,
                            force_ocr: bool = False) -> DocumentConverter:
    """
    创建自定义 Docling 管线

    Args:
        use_qwen_ocr: 是否使用 Qwen VL 作为 OCR 后端
        ocr_enabled: 是否启用 OCR
        force_ocr: 是否强制使用 OCR（即使 PDF 有文本层）

    Returns:
        配置好的 DocumentConverter
    """
    # Configure PDF pipeline
    pipeline_options = PdfPipelineOptions(
        do_ocr=ocr_enabled,
        do_table_structure=True,  # 启用表格结构识别
        images_scale=2.0,  # 图片缩放比例
        generate_page_images=force_ocr,  # 强制生成页面图片用于 OCR
        generate_picture_images=True,
    )

    # Create converter with custom pipeline
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
                backend=PyPdfiumDocumentBackend,
            )
        }
    )

    return converter


def process_pdf_with_qwen_fallback(pdf_path: str, output_path: Optional[str] = None) -> str:
    """
    使用 Docling 处理 PDF，失败时使用 Qwen VL 作为后备方案

    Args:
        pdf_path: PDF 文件路径
        output_path: 输出文件路径

    Returns:
        提取的 Markdown 内容
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    print(f"📄 Processing PDF: {pdf_path.name}")
    print("=" * 80)

    # Step 1: Try standard Docling pipeline
    print("\n🔄 Step 1: Trying standard Docling pipeline...")
    try:
        converter = create_docling_pipeline(use_qwen_ocr=False, ocr_enabled=True)
        result = converter.convert(str(pdf_path))
        markdown_content = result.document.export_to_markdown()

        # Check if extraction was successful
        if len(markdown_content.strip()) > 100:
            print("✅ Docling extraction successful!")
            print(f"   Extracted {len(markdown_content)} characters")
            return markdown_content
        else:
            print("⚠️  Docling extracted insufficient content, trying Qwen VL...")
    except Exception as e:
        print(f"⚠️  Docling pipeline failed: {e}")
        print("🔄 Falling back to Qwen VL OCR...")

    # Step 2: Use Qwen VL as fallback
    if not QWEN_AVAILABLE or not IMAGE_SUPPORT:
        raise RuntimeError("Qwen VL fallback requires: pip install dashscope pymupdf pillow")

    print("\n🤖 Step 2: Using Qwen VL OCR...")
    try:
        qwen_backend = QwenOCRBackend()

        # Convert PDF to images
        doc = fitz.open(str(pdf_path))
        print(f"   Converting {len(doc)} pages to images...")

        all_text = []
        for page_num in range(len(doc)):
            print(f"   Processing page {page_num + 1}/{len(doc)}...", end=" ")

            # Render page as image
            page = doc[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scale
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))

            # Extract text using Qwen VL
            page_text = qwen_backend.extract_text_from_image(img)
            all_text.append(f"## Page {page_num + 1}\n\n{page_text}\n")
            print("✓")

        doc.close()

        markdown_content = "\n".join(all_text)
        print(f"\n✅ Qwen VL extraction successful!")
        print(f"   Extracted {len(markdown_content)} characters")
        return markdown_content

    except Exception as e:
        raise RuntimeError(f"Qwen VL OCR failed: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Docling custom pipeline with Qwen VL OCR integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with standard Docling pipeline
  python docling_qwen_pipeline.py document.pdf
  
  # Force Qwen VL OCR (requires DASHSCOPE_API_KEY)
  export DASHSCOPE_API_KEY="your-api-key"
  python docling_qwen_pipeline.py document.pdf --use-qwen
  
  # Custom output path
  python docling_qwen_pipeline.py document.pdf -o output.md
  
  # Enable OCR for all pages
  python docling_qwen_pipeline.py document.pdf --force-ocr

Environment Variables:
  DASHSCOPE_API_KEY    API key for Qwen VL (get from dashscope.console.aliyun.com)
  QWEN_MODEL          Qwen model to use (default: qwen-vl-max)
        """
    )
    parser.add_argument("pdf", help="Path to PDF file or URL")
    parser.add_argument("--output", "-o", help="Output markdown file (default: <pdf_name>_output.md)")
    parser.add_argument("--use-qwen", action="store_true", help="Force use Qwen VL OCR")
    parser.add_argument("--force-ocr", action="store_true", help="Force OCR even if PDF has text layer")
    parser.add_argument("--no-ocr", action="store_true", help="Disable OCR completely")
    parser.add_argument("--preview-only", action="store_true", help="Only show preview, don't save file")

    args = parser.parse_args()

    try:
        # Process PDF
        if args.use_qwen:
            # Force Qwen VL pipeline
            if not QWEN_AVAILABLE:
                print("❌ Qwen VL not available. Install with: pip install dashscope", file=sys.stderr)
                sys.exit(1)
            content = process_pdf_with_qwen_fallback(args.pdf)
        else:
            # Standard Docling pipeline with auto-fallback
            pdf_path = Path(args.pdf) if not args.pdf.startswith('http') else args.pdf

            print(f"📄 Processing: {Path(args.pdf).name if not args.pdf.startswith('http') else args.pdf}")
            print("=" * 80)

            converter = create_docling_pipeline(
                use_qwen_ocr=False,
                ocr_enabled=not args.no_ocr,
                force_ocr=args.force_ocr
            )

            result = converter.convert(args.pdf)
            content = result.document.export_to_markdown()

            # Check if extraction was successful
            if len(content.strip()) < 100:
                print("\n⚠️  Standard pipeline extracted insufficient content")
                print("🔄 Retrying with Qwen VL fallback...")
                content = process_pdf_with_qwen_fallback(args.pdf)
            else:
                print(f"\n✅ Extraction successful! ({len(content)} characters)")

        # Display preview
        print("\n" + "=" * 80)
        print("📝 CONTENT PREVIEW (first 500 characters):")
        print("=" * 80)
        preview = content[:500] + "..." if len(content) > 500 else content
        print(preview)
        print("=" * 80)

        # Save to file
        if not args.preview_only:
            if args.output:
                output_path = Path(args.output)
            else:
                pdf_name = Path(args.pdf).stem if not args.pdf.startswith('http') else "output"
                output_path = Path(f"{pdf_name}_output.md")

            output_path.write_text(content, encoding='utf-8')
            print(f"\n💾 Saved to: {output_path.absolute()}")
        else:
            print("\n💡 Preview mode: file not saved")

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
