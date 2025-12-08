#!/bin/bash

# Script para configurar ArgoCD con las aplicaciones de AuthService

echo "🔧 Configurando ArgoCD para AuthService..."
ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)

# Login a ArgoCD (asumiendo que está instalado y accesible)
argocd login localhost:8080 --username admin --password $ARGOCD_PASSWORD --insecure

# Crear proyecto de ArgoCD
echo "📁 Creando proyecto AuthService..."
kubectl apply -f argocd-project.yaml

# Crear aplicaciones de ArgoCD
echo "🚀 Creando aplicaciones de ArgoCD..."
kubectl apply -f argocd-application-dev.yaml
kubectl apply -f argocd-application-prod.yaml

# Esperar a que las aplicaciones se creen
echo "⏳ Esperando a que las aplicaciones se sincronicen..."
sleep 10

# Forzar sincronización inicial
argocd app sync authservice-dev --force --prune
argocd app sync authservice-prod --force --prune

# Esperar a que se complete la sincronización
argocd app wait authservice-dev --timeout 300
argocd app wait authservice-prod --timeout 300

echo "✅ Configuración de ArgoCD completada!"
echo "📊 Verifica el estado en: https://localhost:8080"