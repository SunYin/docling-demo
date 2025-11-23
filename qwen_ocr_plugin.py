#!/usr/bin/env python3
"""
Qwen VL OCR 插件 for Docling
实现 BaseOcrModel 接口，作为 Docling 管线的一部分
"""
import os
import tempfile
from typing import Iterable, Optional

from PIL import Image
from dotenv import load_dotenv

# Docling imports
from docling.models.base_ocr_model import BaseOcrModel
from docling.datamodel.base_models import Page, BoundingBox, TextCell, AssembledUnit
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import OcrOptions, AcceleratorOptions

# Qwen imports
try:
    import dashscope
    from dashscope import MultiModalConversation
    QWEN_AVAILABLE = True
except ImportError:
    QWEN_AVAILABLE = False
    raise ImportError("dashscope not installed. Install with: pip install dashscope")

load_dotenv()


class QwenOcrModel(BaseOcrModel):
    """
    Qwen VL OCR 模型 - 作为 Docling 管线的 OCR 引擎

    实现 BaseOcrModel 接口，可以直接集成到 Docling 处理管线中
    """

    def __init__(
        self,
        enabled: bool = True,
        api_key: Optional[str] = None,
        model: str = "qwen-vl-max",
        options: Optional[OcrOptions] = None,
        accelerator_options: Optional[AcceleratorOptions] = None,
        **kwargs
    ):
        """
        初始化 Qwen OCR 模型

        Args:
            enabled: 是否启用
            api_key: DashScope API Key
            model: Qwen VL 模型名称
            options: OCR 选项
            accelerator_options: 加速器选项
        """
        # 创建默认选项
        if options is None:
            options = OcrOptions(lang=["en", "zh"])
        if accelerator_options is None:
            accelerator_options = AcceleratorOptions()

        # 调用父类初始化
        super().__init__(
            enabled=enabled,
            artifacts_path=None,
            options=options,
            accelerator_options=accelerator_options
        )

        self.api_key = api_key or os.getenv('DASHSCOPE_API_KEY')
        if not self.api_key:
            raise ValueError(
                "DASHSCOPE_API_KEY not found. "
                "Set it in .env file or pass as api_key parameter."
            )

        dashscope.api_key = self.api_key
        self.model = model
        print(f"✓ Qwen VL OCR Plugin initialized (model: {model})")

    def __call__(
        self,
        conv_res: ConversionResult,
        page_batch: Iterable[Page]
    ) -> Iterable[Page]:
        """
        对页面批次进行 OCR 处理

        这是 Docling 管线调用的主接口

        Args:
            conv_res: 转换结果对象
            page_batch: 页面批次

        Yields:
            处理后的页面对象
        """
        for page in page_batch:
            try:
                # 获取页面图片
                if page.image is None:
                    print(f"⚠️  Page {page.page_no} has no image, skipping OCR")
                    yield page
                    continue

                print(f"🤖 Processing page {page.page_no} with Qwen VL OCR...")

                # 使用 Qwen VL 进行 OCR
                text = self._ocr_image(page.image)

                if text:
                    # 创建 TextCell 包含 OCR 文本
                    text_cell = TextCell(
                        text=text,
                        bbox=BoundingBox(
                            l=0,
                            t=0,
                            r=page.size.width if page.size else 1000,
                            b=page.size.height if page.size else 1000
                        )
                    )

                    # 创建或更新 assembled 字段
                    if page.assembled is None:
                        page.assembled = AssembledUnit(elements=[])

                    # 将文本添加到 assembled 单元
                    page.assembled.elements.append(text_cell)

                    print(f"✓ Extracted {len(text)} characters from page {page.page_no}")
                else:
                    print(f"⚠️  No text extracted from page {page.page_no}")

                yield page

            except Exception as e:
                print(f"❌ Error processing page {page.page_no}: {e}")
                yield page

    def _ocr_image(self, image: Image.Image, prompt: Optional[str] = None) -> str:
        """
        使用 Qwen VL API 对图片进行 OCR

        Args:
            image: PIL Image 对象
            prompt: 自定义提示词

        Returns:
            识别的文本
        """
        # 保存图片到临时文件（Qwen API 需要文件路径）
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            image.save(tmp, format='PNG')
            tmp_path = tmp.name

        try:
            # 默认 OCR 提示词
            if prompt is None:
                prompt = "请识别图片中的所有文字内容，保持原有格式和布局。只返回文字内容，不要添加任何解释。"

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
                # 提取文本内容
                content = response.output.choices[0].message.content
                if isinstance(content, list):
                    text_parts = [item.get('text', '') for item in content if 'text' in item]
                    return '\n'.join(text_parts)
                elif isinstance(content, str):
                    return content
                else:
                    return str(content)
            else:
                print(f"⚠️  Qwen API error: {response.message}")
                return ""

        except Exception as e:
            print(f"⚠️  OCR error: {e}")
            return ""
        finally:
            # 清理临时文件
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


# 插件注册信息（用于 Docling 插件系统）
__docling_plugin__ = {
    'name': 'qwen',
    'version': '1.0.0',
    'description': 'Qwen VL OCR Engine for Docling',
    'model_class': QwenOcrModel,
}

