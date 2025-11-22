#!/bin/bash
# Kubernetes 快速部署脚本

set -e

echo "🚀 Docling K8s 部署工具"
echo ""
echo "请选择部署方案："
echo "  1) 使用镜像内置模型（快速，镜像较大）"
echo "  2) 使用共享 PVC（推荐生产环境）"
echo ""
read -p "请输入选项 (1/2): " choice

case $choice in
  1)
    echo ""
    echo "📦 方案 1: 使用镜像内置模型"
    echo ""

    # 检查镜像是否存在
    read -p "请输入镜像地址 (例: your-registry/docling-demo:latest): " IMAGE

    # 修改 deployment.yaml 中的镜像地址
    sed -i.bak "s|image:.*|image: $IMAGE|g" k8s/deployment.yaml

    # 注释掉卷挂载
    echo "正在配置 deployment..."

    # 部署应用
    kubectl apply -f k8s/deployment.yaml

    echo ""
    echo "✅ 部署完成！"
    echo ""
    echo "查看状态: kubectl get pods -l app=docling"
    echo "查看日志: kubectl logs -l app=docling -f"
    ;;

  2)
    echo ""
    echo "📦 方案 2: 使用共享 PVC"
    echo ""

    # 部署 PVC
    echo "创建 PVC..."
    kubectl apply -f k8s/pvc.yaml

    # 等待 Job 完成
    echo "等待模型下载完成（可能需要 10-20 分钟）..."
    kubectl wait --for=condition=complete job/docling-model-downloader --timeout=30m || {
      echo "❌ 模型下载超时或失败"
      echo "查看日志: kubectl logs job/docling-model-downloader"
      exit 1
    }

    echo "✅ 模型下载完成"

    # 检查镜像地址
    read -p "请输入镜像地址 (例: your-registry/docling-demo:latest): " IMAGE
    sed -i.bak "s|image:.*|image: $IMAGE|g" k8s/deployment.yaml

    # 部署应用
    echo "部署应用..."
    kubectl apply -f k8s/deployment.yaml

    echo ""
    echo "✅ 部署完成！"
    echo ""
    echo "查看状态: kubectl get pods -l app=docling"
    echo "查看日志: kubectl logs -l app=docling -f"
    echo "查看 PVC: kubectl get pvc docling-models-pvc"
    ;;

  *)
    echo "无效选项"
    exit 1
    ;;
esac

