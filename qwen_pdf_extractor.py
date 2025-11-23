"""
使用 Qwen VLM API 处理受保护或扫描 PDF
适用于无法直接提取文字的 PDF 文件
"""
import os
import base64
from pathlib import Path
from typing import List, Optional
import fitz  # PyMuPDF
from PIL import Image
import io
from dotenv import load_dotenv
import dashscope
from dashscope import MultiModalConversation

# 加载环境变量
load_dotenv()


class QwenPDFExtractor:
    """使用 Qwen VLM API 提取 PDF 内容"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Qwen PDF 提取器

        Args:
            api_key: DashScope API Key，如不提供则从环境变量读取
        """
        self.api_key = api_key or os.getenv('DASHSCOPE_API_KEY')
        if not self.api_key:
            raise ValueError("请设置 DASHSCOPE_API_KEY 环境变量或传入 api_key 参数")

        dashscope.api_key = self.api_key
        self.model = os.getenv('QWEN_MODEL', 'qwen-vl-max')

    def pdf_to_images(self, pdf_path: str, dpi: int = 300) -> List[Image.Image]:
        """
        将 PDF 转换为图片列表

        Args:
            pdf_path: PDF 文件路径
            dpi: 图片分辨率，默认 300

        Returns:
            PIL Image 对象列表
        """
        print(f"📄 正在转换 PDF: {pdf_path}")

        doc = fitz.open(pdf_path)
        images = []

        for page_num in range(len(doc)):
            print(f"  - 转换第 {page_num + 1}/{len(doc)} 页...")
            page = doc[page_num]

            # 将页面渲染为图片
            mat = fitz.Matrix(dpi / 72, dpi / 72)  # 缩放矩阵
            pix = page.get_pixmap(matrix=mat)

            # 转换为 PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            images.append(img)

        doc.close()
        print(f"✅ 共转换 {len(images)} 页")
        return images

    def image_to_base64(self, image: Image.Image) -> str:
        """将 PIL Image 转换为 base64 字符串"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def extract_text_from_image(self, image: Image.Image, prompt: Optional[str] = None) -> str:
        """
        使用 Qwen VLM 从图片中提取文字

        Args:
            image: PIL Image 对象
            prompt: 自定义提示词

        Returns:
            提取的文字内容
        """
        if prompt is None:
            prompt = """请提取图片中的所有文字内容，按照原始排版格式输出。

要求：
1. 保持原有的段落结构和排版
2. 保留标题、列表、表格等格式
3. 如果有表格，用 Markdown 表格格式输出
4. 不要添加任何额外的说明或注释
5. 直接输出提取的文字内容"""

        # 转换图片为 base64
        img_base64 = self.image_to_base64(image)

        # 调用 Qwen VLM API
        messages = [
            {
                'role': 'user',
                'content': [
                    {'image': f'data:image/png;base64,{img_base64}'},
                    {'text': prompt}
                ]
            }
        ]

        response = MultiModalConversation.call(
            model=self.model,
            messages=messages
        )

        if response.status_code == 200:
            return response.output.choices[0].message.content[0]['text']
        else:
            raise Exception(f"API 调用失败: {response.code} - {response.message}")

    def extract_pdf(
        self,
        pdf_path: str,
        output_format: str = 'markdown',
        dpi: int = 300,
        prompt: Optional[str] = None
    ) -> str:
        """
        提取 PDF 全部内容

        Args:
            pdf_path: PDF 文件路径
            output_format: 输出格式，'markdown' 或 'text'
            dpi: PDF 转图片的分辨率
            prompt: 自定义提示词

        Returns:
            提取的文字内容
        """
        print(f"\n🚀 开始处理 PDF: {Path(pdf_path).name}")
        print(f"⚙️  配置: 模型={self.model}, DPI={dpi}")

        # 转换 PDF 为图片
        images = self.pdf_to_images(pdf_path, dpi=dpi)

        # 提取每页内容
        all_text = []
        for i, img in enumerate(images):
            print(f"\n📖 处理第 {i + 1}/{len(images)} 页...")
            try:
                text = self.extract_text_from_image(img, prompt=prompt)
                all_text.append(text)
                print(f"✅ 第 {i + 1} 页提取完成 ({len(text)} 字符)")
            except Exception as e:
                print(f"❌ 第 {i + 1} 页提取失败: {e}")
                all_text.append(f"[第 {i + 1} 页提取失败]")

        # 合并内容
        if output_format == 'markdown':
            result = '\n\n---\n\n'.join(all_text)  # 用分隔线分隔各页
        else:
            result = '\n\n'.join(all_text)

        print(f"\n✅ PDF 处理完成！总字符数: {len(result)}")
        return result

    def save_to_file(self, content: str, output_path: str):
        """保存提取的内容到文件"""
        output_file = Path(output_path)
        output_file.write_text(content, encoding='utf-8')
        print(f"💾 已保存到: {output_path}")


def main():
    """命令行使用示例"""
    import argparse

    parser = argparse.ArgumentParser(description='使用 Qwen VLM API 提取 PDF 内容')
    parser.add_argument('pdf_path', help='PDF 文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径（可选）')
    parser.add_argument('--dpi', type=int, default=300, help='图片分辨率（默认 300）')
    parser.add_argument('--model', default='qwen-vl-max',
                       choices=['qwen-vl-plus', 'qwen-vl-max'],
                       help='使用的模型')

    args = parser.parse_args()

    # 设置模型
    os.environ['QWEN_MODEL'] = args.model

    # 创建提取器
    extractor = QwenPDFExtractor()

    # 提取内容
    content = extractor.extract_pdf(args.pdf_path, dpi=args.dpi)

    # 输出或保存
    if args.output:
        extractor.save_to_file(content, args.output)
    else:
        print("\n" + "="*50)
        print("提取的内容:")
        print("="*50)
        print(content)


if __name__ == "__main__":
    main()

