#!/usr/bin/env python3
"""
简单测试脚本：测试 Qwen OCR 插件是否正常工作
"""
import os
import sys

def test_plugin_import():
    """测试插件导入"""
    print("=" * 60)
    print("测试 1: 插件导入")
    print("=" * 60)
    try:
        from qwen_ocr_plugin import QwenOcrModel
        print("✅ 插件导入成功")
        return True
    except Exception as e:
        print(f"❌ 插件导入失败: {e}")
        return False


def test_integrated_script():
    """测试集成脚本"""
    print("\n" + "=" * 60)
    print("测试 2: 集成脚本")
    print("=" * 60)
    try:
        from docling_qwen_integrated import create_qwen_pipeline
        print("✅ 集成脚本导入成功")
        return True
    except Exception as e:
        print(f"❌ 集成脚本导入失败: {e}")
        return False


def test_api_key():
    """测试 API Key 配置"""
    print("\n" + "=" * 60)
    print("测试 3: API Key 配置")
    print("=" * 60)

    api_key = os.getenv('DASHSCOPE_API_KEY')
    if api_key:
        print(f"✅ API Key 已配置: {api_key[:10]}...{api_key[-4:]}")
        return True
    else:
        print("⚠️  API Key 未配置")
        print("   设置方法: export DASHSCOPE_API_KEY='your-key'")
        return False


def test_docling_basic():
    """测试基础 Docling 功能"""
    print("\n" + "=" * 60)
    print("测试 4: Docling 基础功能")
    print("=" * 60)
    try:
        from docling.document_converter import DocumentConverter
        print("✅ Docling 导入成功")
        return True
    except Exception as e:
        print(f"❌ Docling 导入失败: {e}")
        return False


def main():
    print("\n🧪 Qwen OCR 插件测试套件\n")

    results = []

    # 运行所有测试
    results.append(("插件导入", test_plugin_import()))
    results.append(("集成脚本", test_integrated_script()))
    results.append(("API Key", test_api_key()))
    results.append(("Docling", test_docling_basic()))

    # 显示摘要
    print("\n" + "=" * 60)
    print("📊 测试摘要")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name:15} {status}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！插件已准备就绪。")
        print("\n下一步:")
        print("  1. 设置 API Key: export DASHSCOPE_API_KEY='your-key'")
        print("  2. 运行示例: python docling_qwen_integrated.py document.pdf")
    else:
        print("\n⚠️  部分测试失败，请检查依赖是否安装完整。")
        print("\n安装命令:")
        print("  pip install docling dashscope pymupdf pillow python-dotenv")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

