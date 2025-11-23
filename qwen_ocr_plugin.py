#!/usr/bin/env python3
"""
Qwen VL OCR 插件 for Docling
实现 BaseOcrModel 接口，作为 Docling 管线的一部分
支持并行处理以提高速度
"""
import os
import tempfile
from typing import Iterable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image
from dotenv import load_dotenv

# Docling imports
from docling.models.base_ocr_model import BaseOcrModel
from docling.datamodel.base_models import Page, AssembledUnit
from docling_core.types.doc import BoundingBox, CoordOrigin
from docling_core.types.doc.page import TextCell, BoundingRectangle
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


class QwenOcrOptions(OcrOptions):
    """Qwen VL OCR 选项"""
    kind: str = "qwen"  # OCR 引擎类型标识
    model_name: str = "qwen-vl-max"  # Qwen 模型名称


class QwenOcrModel(BaseOcrModel):
    """
    Qwen VL OCR 模型 - 作为 Docling 管线的 OCR 引擎

    实现 BaseOcrModel 接口，可以直接集成到 Docling 处理管线中
    """

    @staticmethod
    def get_options_type():
        """返回此 OCR 模型使用的选项类型"""
        return QwenOcrOptions

    def __init__(
        self,
        enabled: bool = True,
        api_key: Optional[str] = None,
        model: str = "qwen-vl-max",
        options: Optional[QwenOcrOptions] = None,
        accelerator_options: Optional[AcceleratorOptions] = None,
        **kwargs
    ):
        """
        初始化 Qwen OCR 模型

        Args:
            enabled: 是否启用
            api_key: DashScope API Key
            model: Qwen VL 模型名称 (如果 options 中有指定，优先使用 options 中的)
            options: OCR 选项
            accelerator_options: 加速器选项
        """
        # 创建默认选项
        if options is None:
            options = QwenOcrOptions(lang=["en", "zh"])
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
        
        # 优先使用 options 中的 model_name
        if isinstance(options, QwenOcrOptions) and options.model_name:
            self.model = options.model_name
        else:
            self.model = model
            
        print(f"✓ Qwen VL OCR Plugin initialized (model: {self.model})")

    def __call__(
        self,
        conv_res: ConversionResult,
        page_batch: Iterable[Page]
    ) -> Iterable[Page]:
        """
        对页面批次进行 OCR 处理（并行）

        这是 Docling 管线调用的主接口

        Args:
            conv_res: 转换结果对象
            page_batch: 页面批次

        Yields:
            处理后的页面对象
        """
        pages = list(page_batch)
        
        if not pages:
            return
        
        print(f"🚀 并行处理 {len(pages)} 页...")
        
        # 使用线程池并行处理所有页面
        with ThreadPoolExecutor(max_workers=len(pages)) as executor:
            # 提交所有任务
            future_to_page = {
                executor.submit(self._process_single_page, page): page 
                for page in pages
            }
            
            # 按完成顺序收集结果
            for future in as_completed(future_to_page):
                page = future_to_page[future]
                try:
                    processed_page = future.result()
                    yield processed_page
                except Exception as e:
                    print(f"❌ Error processing page {page.page_no}: {e}")
                    yield page
    
    def _process_single_page(self, page: Page) -> Page:
        """
        处理单个页面（在线程池中调用）
        
        Args:
            page: 要处理的页面
            
        Returns:
            处理后的页面
        """
        try:
            # 获取页面图片
            if page.image is None:
                print(f"⚠️  Page {page.page_no} has no image, skipping OCR")
                return page

            print(f"🤖 Processing page {page.page_no} with Qwen VL OCR...")

            # 使用 Qwen VL 进行 OCR
            text = self._ocr_image(page.image)

            if text:
                # 创建 TextCell 包含 OCR 文本
                # 获取页面尺寸
                width = page.size.width if page.size else 1000
                height = page.size.height if page.size else 1000
                
                # 创建 BoundingRectangle
                rect = BoundingRectangle(
                    r_x0=0, r_y0=0,
                    r_x1=width, r_y1=0,
                    r_x2=width, r_y2=height,
                    r_x3=0, r_y3=height,
                    coord_origin=CoordOrigin.TOPLEFT
                )
                
                text_cell = TextCell(
                    text=text,
                    orig=text,  # 原始文本
                    rect=rect,
                    from_ocr=True,
                    confidence=1.0
                )

                # 使用 BaseOcrModel 的 post_process_cells 方法更新页面
                # 这会将 OCR 结果合并到 page.parsed_page.textline_cells 中
                # 从而被后续的 LayoutModel 和 PageAssembleModel 正确处理
                self.post_process_cells([text_cell], page)

                print(f"✓ Extracted {len(text)} characters from page {page.page_no}")
            else:
                print(f"⚠️  No text extracted from page {page.page_no}")

            return page

        except Exception as e:
            print(f"❌ Error processing page {page.page_no}: {e}")
            return page

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
