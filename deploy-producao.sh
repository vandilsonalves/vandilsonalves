#!/bin/bash
# ================================================================
# Script de Deploy Producao - Ranking Run Pro
# Inclui: SSL (Let's Encrypt) + mTLS (Efi Bank) + App
# ================================================================
# Uso:
#   chmod +x deploy-producao.sh
#   ./deploy-producao.sh rankingrun.com.br admin@rankingrun.com.br
# ================================================================

set -e

DOMAIN="${1:-rankingrun.com.br}"
EMAIL="${2:-admin@rankingrun.com.br}"
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
CERTS_DIR="$APP_DIR/backend/certs"
NGINX_CONF="$APP_DIR/backend/nginx/nginx-mtls.conf"

echo ""
echo "============================================"
echo "  Deploy Producao - Ranking Run Pro"
echo "  Dominio: $DOMAIN"
echo "  Email: $EMAIL"
echo "============================================"
echo ""

# 1. Verificar Docker
echo "[1/7] Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo "  Docker nao encontrado. Instalando..."
    curl -fsSL https://get.docker.com | sh
fi
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "  Docker Compose nao encontrado. Instalando..."
    apt-get install -y docker-compose-plugin 2>/dev/null || pip install docker-compose
fi
echo "  OK: Docker instalado"

# 2. Verificar DNS
echo ""
echo "[2/7] Verificando DNS..."
RESOLVED_IP=$(dig +short A $DOMAIN @8.8.8.8 | head -1)
SERVER_IP=$(curl -s ifconfig.me)
if [ "$RESOLVED_IP" != "$SERVER_IP" ]; then
    echo "  AVISO: $DOMAIN resolve para $RESOLVED_IP mas este servidor e $SERVER_IP"
    echo "  O Let's Encrypt pode falhar se o DNS nao apontar para este servidor."
    read -p "  Continuar mesmo assim? (s/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
else
    echo "  OK: $DOMAIN -> $SERVER_IP (correto)"
fi

# 3. Gerar certificados SSL (Let's Encrypt)
echo ""
echo "[3/7] Gerando certificados SSL (Let's Encrypt)..."
SSL_CERT="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
SSL_KEY="/etc/letsencrypt/live/$DOMAIN/privkey.pem"

if [ -f "$SSL_CERT" ] && [ -f "$SSL_KEY" ]; then
    echo "  Certificados SSL ja existem. Renovando..."
    certbot renew --quiet || true
else
    # Parar qualquer servico na porta 80
    docker stop rankingrun-mtls-proxy 2>/dev/null || true
    fuser -k 80/tcp 2>/dev/null || true
    
    if ! command -v certbot &> /dev/null; then
        apt-get update && apt-get install -y certbot
    fi
    
    certbot certonly --standalone \
        -d $DOMAIN \
        --non-interactive \
        --agree-tos \
        --email $EMAIL \
        --preferred-challenges http || {
        echo "  ERRO: Falha ao gerar certificados SSL."
        echo "  Verifique se a porta 80 esta liberada e o DNS aponta para este servidor."
        exit 1
    }
fi

# Copiar para diretorio do app
cp "$SSL_CERT" "$CERTS_DIR/fullchain.pem"
cp "$SSL_KEY" "$CERTS_DIR/privkey.pem"
echo "  OK: Certificados SSL gerados e copiados"

# 4. Verificar certificados CA do Efi Bank
echo ""
echo "[4/7] Verificando certificados CA do Efi Bank..."
if [ ! -f "$CERTS_DIR/efi-ca-prod.crt" ]; then
    echo "  Baixando efi-ca-prod.crt..."
    curl -sL "https://raw.githubusercontent.com/efipay/mtls-webhook/main/certs/prod.crt" \
        -o "$CERTS_DIR/efi-ca-prod.crt"
fi
echo "  OK: Certificados CA presentes"

# 5. Atualizar nginx.conf com o dominio
echo ""
echo "[5/7] Configurando Nginx..."
sed -i "s/server_name .*/server_name $DOMAIN;/" "$NGINX_CONF"
echo "  OK: Nginx configurado para $DOMAIN"

# 6. Build e deploy
echo ""
echo "[6/7] Construindo e iniciando containers..."
cd "$APP_DIR"
docker compose -f docker-compose.mtls.yml down 2>/dev/null || true
docker compose -f docker-compose.mtls.yml up -d --build
echo "  OK: Containers iniciados"

# 7. Verificar
echo ""
echo "[7/7] Verificando servicos..."
sleep 5
if curl -sk "https://$DOMAIN/api/health" 2>/dev/null | grep -q "ok\|healthy"; then
    echo "  OK: API respondendo"
else
    echo "  AVISO: API ainda inicializando. Verifique em alguns segundos."
fi

echo ""
echo "============================================"
echo "  Deploy concluido com sucesso!"
echo "============================================"
echo ""
echo "  App:     https://$DOMAIN"
echo "  API:     https://$DOMAIN/api"
echo "  Webhook: https://$DOMAIN/api/efi/webhook/pix"
echo ""
echo "  Proximo passo:"
echo "  Registre o webhook no Efi Bank usando o endpoint admin:"
echo "  curl -X POST https://$DOMAIN/api/efi/admin/webhook/registrar \\"
echo "    -H 'Authorization: Bearer <TOKEN>' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"modo\": \"mtls\"}'"
echo ""
echo "  Para renovar SSL: certbot renew --quiet"
echo "  Logs: docker logs rankingrun-mtls-proxy -f"
echo "============================================"
