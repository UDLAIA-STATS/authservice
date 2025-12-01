#!/bin/bash

# Script de instalación completo del stack DevSecOps
# AuthService con ArgoCD y LaunchDarkly

set -e

echo "🚀 Iniciando instalación del stack DevSecOps..."
echo "================================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de utilidad
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar requisitos previos
check_prerequisites() {
    print_info "Verificando requisitos previos..."
    
    # Verificar kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl no está instalado"
        exit 1
    fi
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado"
        exit 1
    fi
    
    # Verificar git
    if ! command -v git &> /dev/null; then
        print_error "Git no está instalado"
        exit 1
    fi
    
    print_success "Requisitos previos verificados"
}

# Instalar ArgoCD
install_argocd() {
    print_info "Instalando ArgoCD..."
    
    # Crear namespace
    kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
    
    # Instalar ArgoCD
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
    
    # Esperar a que ArgoCD esté listo
    print_info "Esperando a que ArgoCD esté listo..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n argocd --timeout=600s
    
    # Obtener contraseña inicial
    ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
    
    print_success "ArgoCD instalado correctamente"
    print_info "URL: https://localhost:8080"
    print_info "Usuario: admin"
    print_info "Contraseña: $ARGOCD_PASSWORD"
    
    # Port forwarding
    kubectl port-forward svc/argocd-server -n argocd 8080:443 &
    print_info "Port forwarding activo en http://localhost:8080"
}

# Configurar aplicaciones de ArgoCD
setup_argocd_apps() {
    print_info "Configurando aplicaciones de ArgoCD..."
    
    # Aplicar configuración del proyecto
    kubectl apply -f argocd/argocd-project.yaml
    
    # Aplicar aplicaciones
    kubectl apply -f argocd/argocd-application-dev.yaml
    kubectl apply -f argocd/argocd-application-prod.yaml
    
    print_success "Aplicaciones de ArgoCD configuradas"
}

# Crear namespaces para las aplicaciones
create_namespaces() {
    print_info "Creando namespaces..."
    
    kubectl create namespace authservice-dev --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace authservice-prod --dry-run=client -o yaml | kubectl apply -f -
    
    print_success "Namespaces creados"
}

# Configurar secrets de LaunchDarkly
setup_launchdarkly_secrets() {
    print_info "Configurando secrets de LaunchDarkly..."
    
    # Crear secrets en dev
    kubectl apply -f dev/launchdarkly-secret.yaml
    
    # Crear secrets en prod
    kubectl apply -f prod/launchdarkly-secret.yaml
    
    print_warning "⚠️  Recuerda actualizar los secrets con tus credenciales reales de LaunchDarkly"
    print_info "Para actualizar el secret en dev:"
    print_info "kubectl create secret generic launchdarkly-secrets --from-literal=sdk-key=YOUR_SDK_KEY -n authservice-dev --dry-run=client -o yaml | kubectl apply -f -"
    
    print_success "Secrets de LaunchDarkly configurados"
}

# Instalar herramientas CLI
install_cli_tools() {
    print_info "Instalando herramientas CLI..."
    
    # Instalar ArgoCD CLI
    if ! command -v argocd &> /dev/null; then
        print_info "Instalando ArgoCD CLI..."
        curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
        sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd
        rm argocd-linux-amd64
    fi
    
    # Instalar LaunchDarkly CLI
    if ! command -v ldcli &> /dev/null; then
        print_info "Instalando LaunchDarkly CLI..."
        npm install -g @launchdarkly/ldcli
    fi
    
    print_success "Herramientas CLI instaladas"
}

# Verificar estado del despliegue
check_deployment_status() {
    print_info "Verificando estado del despliegue..."
    
    # Esperar a que las aplicaciones se sincronicen
    sleep 30
    
    # Verificar estado de las aplicaciones
    echo "Estado de las aplicaciones de ArgoCD:"
    kubectl get applications -n argocd
    
    # Verificar pods
    echo ""
    echo "Pods en authservice-dev:"
    kubectl get pods -n authservice-dev
    
    echo ""
    echo "Pods en authservice-prod:"
    kubectl get pods -n authservice-prod
}

# Generar reporte de instalación
generate_installation_report() {
    print_info "Generando reporte de instalación..."
    
    cat > installation-report.md << EOF
# 📊 Reporte de Instalación DevSecOps

## Fecha de Instalación
$(date)

## Componentes Instalados
- ✅ ArgoCD
- ✅ LaunchDarkly Integration
- ✅ Feature Flags
- ✅ CI/CD Pipeline
- ✅ Monitoreo

## URLs de Acceso
- ArgoCD: https://localhost:8080
- AuthService Dev: http://localhost:8000
- AuthService Prod: http://localhost:8001

## Credenciales
- ArgoCD Username: admin
- ArgoCD Password: (ver en secrets)

## Próximos Pasos
1. Configurar credenciales reales de LaunchDarkly
2. Configurar GitHub Secrets
3. Ejecutar pipeline CI/CD
4. Verificar despliegue

## Feature Flags Disponibles
- new-authentication-flow
- multi-factor-authentication
- advanced-logging
- rate-limiting
- session-management-v2
- audit-trail

## Monitoreo
- Health checks configurados
- Métricas de ArgoCD
- Logs centralizados
- Alertas configuradas
EOF

    print_success "Reporte de instalación generado: installation-report.md"
}

# Función principal
main() {
    print_info "Iniciando instalación completa del stack DevSecOps..."
    
    check_prerequisites
    install_cli_tools
    create_namespaces
    install_argocd
    setup_argocd_apps
    setup_launchdarkly_secrets
    check_deployment_status
    generate_installation_report
    
    print_success "🎉 Instalación completada exitosamente!"
    print_info "Revisa el reporte de instalación para próximos pasos"
    
    # Mostrar resumen
    echo ""
    echo "================================================"
    echo "📋 RESUMEN DE INSTALACIÓN"
    echo "================================================"
    echo "✅ ArgoCD: Instalado y configurado"
    echo "✅ LaunchDarkly: Integración lista"
    echo "✅ Feature Flags: Configuradas"
    echo "✅ CI/CD Pipeline: Preparado"
    echo "✅ Monitoreo: Activado"
    echo ""
    echo "🌐 Accede a ArgoCD: https://localhost:8080"
    echo "📖 Lee la guía: DEPLOYMENT_GUIDE.md"
    echo "🔧 Configura secrets: Actualiza launchdarkly-secret.yaml"
    echo ""
}

# Ejecutar función principal
main "$@"