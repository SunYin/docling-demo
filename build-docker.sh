#!/bin/bash
# 快速构建和测试 Docker 镜像

set -e

echo "🚀 开始构建 Docling Docker 镜像..."
echo "⚠️  注意：首次构建会下载模型，需要 5-15 分钟，请耐心等待"
echo ""

# 构建镜像
docker build -t docling-demo:latest .

echo ""
echo "✅ 镜像构建完成！"
echo ""
echo "📊 镜像信息："
docker images docling-demo:latest

echo ""
echo "🧪 测试运行容器..."
docker run --rm docling-demo:latest

echo ""
echo "✅ 测试完成！"
echo ""
echo "📚 使用方法："
echo "  - 直接运行: docker run --rm docling-demo:latest"
echo "  - 使用 Docker Compose: docker-compose up"
echo "  - 推送到仓库: docker tag docling-demo:latest your-registry/docling-demo:latest"
echo "               docker push your-registry/docling-demo:latest"

