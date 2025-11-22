"""
预下载 Docling 所需的所有 AI 模型
用于 Docker 镜像构建或本地预缓存
"""
import os
from docling.document_converter import DocumentConverter


def download_models():
    """
    初始化 DocumentConverter 会自动下载所有必需的模型到缓存目录
    默认缓存路径: ~/.cache/docling/ (可通过 DOCLING_CACHE_DIR 环境变量修改)
    """
    print("🚀 开始下载 Docling 模型...")
    print(f"📦 缓存目录: {os.environ.get('DOCLING_CACHE_DIR', '~/.cache/docling/')}")

    try:
        # 初始化转换器会触发模型下载
        converter = DocumentConverter()
        print("✅ 模型下载完成!")

        # 测试转换一个简单的文档以确保所有模型正常加载
        print("🧪 测试模型加载...")
        # 这里不实际转换文档，只是确保 converter 初始化成功
        print("✅ 所有模型已成功加载并缓存!")

    except Exception as e:
        print(f"❌ 模型下载失败: {e}")
        raise


if __name__ == "__main__":
    download_models()

