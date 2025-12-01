#!/bin/bash

# Script para instalar ArgoCD en el cluster de Kubernetes

echo "🔧 Instalando ArgoCD en el cluster Kubernetes..."

# Crear namespace para ArgoCD
kubectl create namespace argocd

# Instalar ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Esperar a que los pods de ArgoCD estén listos
echo "⏳ Esperando a que ArgoCD esté listo..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n argocd --timeout=300s

# Obtener la contraseña inicial de admin
ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)

echo "✅ ArgoCD instalado correctamente!"
echo "🌐 URL de ArgoCD: https://localhost:8080"
echo "👤 Usuario: admin"
echo "🔑 Contraseña: $ARGOCD_PASSWORD"

# Port forwarding para acceso local
kubectl port-forward svc/argocd-server -n argocd 8080:443 &

echo "🚀 Port forwarding activo en http://localhost:8080"
echo "⚠️  No olvides cambiar la contraseña por defecto!"