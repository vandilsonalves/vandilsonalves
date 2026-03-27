#!/bin/bash
# ================================================================
# Script de Deploy mTLS - Efi Bank PIX Webhook
# Ranking Run Pro
# ================================================================
# Uso: chmod +x deploy-mtls.sh && ./deploy-mtls.sh
# ================================================================

set -e

DOMAIN="rankingrun.com.br"
CERTS_DIR="./backend/certs"
NGINX_CONF="./backend/nginx/nginx-mtls.conf"

echo "========================================"
echo " Deploy mTLS - Efi Bank PIX Webhook"
echo " Dominio: $DOMAIN"
echo "========================================"

# 1. Verificar certificados CA do Efi Bank
echo ""
echo "[1/5] Verificando certificados CA do Efi Bank..."
if [ ! -f "$CERTS_DIR/efi-ca-prod.crt" ]; then
    echo "  Baixando efi-ca-prod.crt..."
    curl -sL "https://raw.githubusercontent.com/efipay/mtls-webhook/main/certs/prod.crt" \
        -o "$CERTS_DIR/efi-ca-prod.crt"
fi
echo "  OK: efi-ca-prod.crt presente"

# 2. Verificar certificados SSL do dominio
echo ""
echo "[2/5] Verificando certificados SSL do dominio..."
SSL_CERT="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
SSL_KEY="/etc/letsencrypt/live/$DOMAIN/privkey.pem"

if [ ! -f "$SSL_CERT" ] || [ ! -f "$SSL_KEY" ]; then
    echo "  AVISO: Certificados SSL nao encontrados em $SSL_CERT"
    echo "  Gerando com certbot..."
    certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN || {
        echo "  ERRO: Falha ao gerar certificados. Verifique DNS e porta 80."
        exit 1
    }
fi
echo "  OK: Certificados SSL presentes"

# 3. Copiar certificados SSL para o diretorio de certs
echo ""
echo "[3/5] Copiando certificados SSL..."
cp "$SSL_CERT" "$CERTS_DIR/fullchain.pem"
cp "$SSL_KEY" "$CERTS_DIR/privkey.pem"
echo "  OK: Certificados copiados"

# 4. Testar configuracao Nginx
echo ""
echo "[4/5] Testando configuracao Nginx..."
nginx -t -c "$(pwd)/$NGINX_CONF" 2>&1 || {
    echo "  AVISO: Teste nginx -t falhou (normal se nao for o ambiente final)"
    echo "  A configuracao sera validada pelo Docker"
}

# 5. Deploy
echo ""
echo "[5/5] Iniciando containers..."
docker-compose -f docker-compose.mtls.yml up -d --build
echo "  OK: Containers iniciados"

echo ""
echo "========================================"
echo " Deploy concluido!"
echo "========================================"
echo ""
echo " Webhook URL: https://$DOMAIN/api/efi/webhook/pix"
echo ""
echo " Proximo passo: Registrar webhook no Efi Bank"
echo " Use o endpoint admin: POST /api/efi/admin/webhook/registrar"
echo " (Remova o header x-skip-mtls-checking para usar mTLS real)"
echo ""
echo " Para verificar status: curl -v https://$DOMAIN/api/efi/webhook/pix"
echo " Logs: docker logs rankingrun-mtls-proxy -f"
echo "========================================"
