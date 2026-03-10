# /app/backend/tasks/email_tasks.py
"""
Tarefas de Email para processamento em background
"""

from celery_app import celery_app
import logging
import os

logger = logging.getLogger(__name__)


def get_db():
    from pymongo import MongoClient
    client = MongoClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
    return client[os.environ.get('DB_NAME', 'test_database')]


@celery_app.task(bind=True, max_retries=3, default_retry_delay=120)
def enviar_email_task(self, destinatario: str, assunto: str, html_content: str):
    """
    Envia um email em background
    """
    try:
        import resend
        
        api_key = os.environ.get('RESEND_API_KEY')
        if not api_key:
            logger.warning("RESEND_API_KEY não configurada")
            return {"status": "skipped", "message": "API key não configurada"}
        
        resend.api_key = api_key
        
        result = resend.Emails.send({
            "from": "Ranking Run Pró <onboarding@resend.dev>",
            "to": [destinatario],
            "subject": assunto,
            "html": html_content
        })
        
        logger.info(f"📧 Email enviado para {destinatario}: {result.get('id', 'OK')}")
        return {"status": "success", "email_id": result.get('id')}
    
    except Exception as e:
        logger.error(f"❌ Erro ao enviar email para {destinatario}: {e}")
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=2)
def enviar_emails_aniversario_task(self, data: str = None):
    """
    Envia emails de aniversário em massa
    """
    try:
        from datetime import datetime
        
        db = get_db()
        hoje = data or datetime.now().strftime("%m-%d")
        
        # Buscar aniversariantes
        pipeline = [
            {"$match": {"role": "atleta", "is_active": True}},
            {"$addFields": {"mes_dia": {"$substr": ["$data_nascimento", 5, 5]}}},
            {"$match": {"mes_dia": hoje}}
        ]
        
        aniversariantes = list(db.usuarios.aggregate(pipeline))
        
        enviados = 0
        erros = 0
        
        for atleta in aniversariantes:
            try:
                html = gerar_email_aniversario(atleta["nome"])
                
                # Disparar como sub-task
                enviar_email_task.delay(
                    atleta["email"],
                    f"🎂 Feliz Aniversário, {atleta['nome'].split()[0]}!",
                    html
                )
                enviados += 1
                
            except Exception as e:
                logger.error(f"Erro ao enviar para {atleta.get('email')}: {e}")
                erros += 1
        
        logger.info(f"🎂 Aniversários: {enviados} emails enfileirados, {erros} erros")
        return {
            "status": "success",
            "total_aniversariantes": len(aniversariantes),
            "emails_enfileirados": enviados,
            "erros": erros
        }
    
    except Exception as e:
        logger.error(f"❌ Erro no envio de aniversários: {e}")
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=2)
def enviar_alerta_sistema_task(self, tipo_alerta: str, detalhes: dict):
    """
    Envia alerta de sistema para administradores
    """
    try:
        db = get_db()
        
        # Buscar super admins
        admins = list(db.admins.find({"role": "super_admin"}, {"email": 1}))
        
        if not admins:
            return {"status": "skipped", "message": "Nenhum admin encontrado"}
        
        html = gerar_email_alerta(tipo_alerta, detalhes)
        
        for admin in admins:
            if admin.get("email"):
                enviar_email_task.delay(
                    admin["email"],
                    f"[ALERTA] {tipo_alerta.upper()} - Ranking Run Pró",
                    html
                )
        
        logger.warning(f"⚠️ Alerta {tipo_alerta} enviado para {len(admins)} admins")
        return {"status": "success", "admins_notificados": len(admins)}
    
    except Exception as e:
        logger.error(f"❌ Erro ao enviar alerta: {e}")
        raise self.retry(exc=e)


def gerar_email_aniversario(nome: str) -> str:
    """Gera HTML do email de aniversário"""
    primeiro_nome = nome.split()[0]
    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; background: #f9fafb; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); padding: 40px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 32px;">🎂 Feliz Aniversário!</h1>
            </div>
            <div style="padding: 40px; text-align: center;">
                <h2 style="color: #111827; margin: 0 0 20px 0;">Parabéns, {primeiro_nome}!</h2>
                <p style="color: #6b7280; font-size: 16px; line-height: 1.6;">
                    A equipe do Ranking Run Pró deseja a você um dia muito especial, 
                    cheio de alegrias, conquistas e muitos quilômetros de felicidade!
                </p>
                <p style="color: #6b7280; font-size: 16px; margin-top: 20px;">
                    Continue correndo e conquistando seus objetivos! 🏃‍♂️🏆
                </p>
            </div>
            <div style="background: #f3f4f6; padding: 20px; text-align: center;">
                <p style="color: #9ca3af; font-size: 12px; margin: 0;">
                    Ranking Run Pró - Sua plataforma de corridas
                </p>
            </div>
        </div>
    </body>
    </html>
    """


def gerar_email_alerta(tipo: str, detalhes: dict) -> str:
    """Gera HTML do email de alerta"""
    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; background: #f9fafb; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden;">
            <div style="background: #dc2626; padding: 24px; text-align: center;">
                <h1 style="color: white; margin: 0;">⚠️ Alerta de Sistema</h1>
            </div>
            <div style="padding: 24px;">
                <h2 style="color: #111827;">Tipo: {tipo}</h2>
                <pre style="background: #f3f4f6; padding: 16px; border-radius: 4px; overflow-x: auto;">
{str(detalhes)}
                </pre>
            </div>
        </div>
    </body>
    </html>
    """
