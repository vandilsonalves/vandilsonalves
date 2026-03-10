#!/bin/bash
# Script para iniciar Celery worker e Flower

# Iniciar worker em background
cd /app/backend
celery -A celery_app worker --loglevel=info -Q default,ranking,email,reports &

# Iniciar Flower (dashboard) em background na porta 5555
celery -A celery_app flower --port=5555 &

echo "Celery worker e Flower iniciados"
