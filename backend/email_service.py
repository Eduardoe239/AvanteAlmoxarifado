"""
Módulo para envio de emails de notificação sobre devoluções de empréstimos.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional


class ConfiguracaoEmail:
    """Configuração do servidor SMTP para envio de emails."""
    
    SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "no-reply@almoxarifado.local")
    EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
    USE_TLS = os.environ.get("EMAIL_USE_TLS", "true").lower() == "true"
    EMAIL_HABILITADO = os.environ.get("EMAIL_HABILITADO", "false").lower() == "true"


def enviar_email_lembrete_devolucao(
    email_destinatario: str,
    nome_usuario: str,
    nome_item: str,
    quantidade: int,
    data_devolucao: datetime,
) -> bool:
    """
    Envia email lembrando ao usuário sobre a devolução 1 dia antes.
    
    Args:
        email_destinatario: Email do usuário
        nome_usuario: Nome completo do usuário
        nome_item: Nome do item emprestado
        quantidade: Quantidade emprestada
        data_devolucao: Data prevista para devolução
        
    Returns:
        bool: True se enviado com sucesso, False caso contrário
    """
    if not ConfiguracaoEmail.EMAIL_HABILITADO or not email_destinatario:
        return False
    
    try:
        assunto = f"⏰ Lembrete: Devolva o item '{nome_item}' amanhã"
        
        corpo_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Olá {nome_usuario}!</h2>
                <p>Este é um lembrete de que você tem <strong>1 dia</strong> para devolver o item emprestado.</p>
                
                <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Item:</strong> {nome_item}</p>
                    <p><strong>Quantidade:</strong> {quantidade}</p>
                    <p><strong>Devolução prevista para:</strong> {data_devolucao.strftime('%d/%m/%Y às %H:%M')}</p>
                </div>
                
                <p>Por favor, certifique-se de devolver o item no prazo indicado.</p>
                <p>Atenciosamente,<br>Sistema de Almoxarifado</p>
            </body>
        </html>
        """
        
        return _enviar_smtp(email_destinatario, assunto, corpo_html)
    except Exception as e:
        print(f"Erro ao enviar lembrete de devolução: {e}")
        return False


def enviar_email_atraso_devolucao(
    email_destinatario: str,
    nome_usuario: str,
    nome_item: str,
    quantidade: int,
    data_devolucao_prevista: datetime,
    dias_atrasado: int,
) -> bool:
    """
    Envia email alertando que a devolução está atrasada.
    
    Args:
        email_destinatario: Email do usuário
        nome_usuario: Nome completo do usuário
        nome_item: Nome do item emprestado
        quantidade: Quantidade emprestada
        data_devolucao_prevista: Data original prevista
        dias_atrasado: Quantos dias passaram da data limite
        
    Returns:
        bool: True se enviado com sucesso, False caso contrário
    """
    if not ConfiguracaoEmail.EMAIL_HABILITADO or not email_destinatario:
        return False
    
    try:
        assunto = f"⚠️ URGENTE: Devolução atrasada - '{nome_item}' com {dias_atrasado} dia(s) de atraso"
        
        corpo_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #d32f2f;">Atenção {nome_usuario}!</h2>
                <p style="color: #d32f2f; font-weight: bold;">A devolução do item está <strong>{dias_atrasado} dia(s) atrasada</strong>!</p>
                
                <div style="background-color: #ffebee; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #d32f2f;">
                    <p><strong>Item:</strong> {nome_item}</p>
                    <p><strong>Quantidade:</strong> {quantidade}</p>
                    <p><strong>Data prevista para devolução:</strong> {data_devolucao_prevista.strftime('%d/%m/%Y às %H:%M')}</p>
                    <p><strong>Dias em atraso:</strong> {dias_atrasado}</p>
                </div>
                
                <p>Por favor, <strong>devolva o item imediatamente</strong>. Atrasos prejudicam outras pessoas que podem precisar do item.</p>
                <p>Caso tenha perdido ou danificado o item, entre em contato com o administrador do sistema.</p>
                <p>Atenciosamente,<br>Sistema de Almoxarifado</p>
            </body>
        </html>
        """
        
        return _enviar_smtp(email_destinatario, assunto, corpo_html)
    except Exception as e:
        print(f"Erro ao enviar alerta de atraso: {e}")
        return False


def _enviar_smtp(email_destinatario: str, assunto: str, corpo_html: str) -> bool:
    """
    Envia email via SMTP.
    
    Args:
        email_destinatario: Email do destinatário
        assunto: Assunto do email
        corpo_html: Corpo em HTML
        
    Returns:
        bool: True se enviado, False caso contrário
    """
    if not ConfiguracaoEmail.EMAIL_HABILITADO:
        return False
    
    try:
        # Criar mensagem
        msg = MIMEMultipart("alternative")
        msg["Subject"] = assunto
        msg["From"] = ConfiguracaoEmail.EMAIL_SENDER
        msg["To"] = email_destinatario
        
        # Versão texto (fallback)
        corpo_texto = corpo_html.replace("<html>", "").replace("</html>", "").replace("<body>", "").replace("</body>", "").replace("<br>", "\n").replace("<p>", "").replace("</p>", "\n").replace("<strong>", "").replace("</strong>", "").replace("<h2>", "").replace("</h2>", "\n").replace("<div>", "").replace("</div>", "\n")
        
        part1 = MIMEText(corpo_texto, "plain")
        part2 = MIMEText(corpo_html, "html")
        
        msg.attach(part1)
        msg.attach(part2)
        
        # Conectar ao servidor SMTP e enviar
        if ConfiguracaoEmail.USE_TLS:
            server = smtplib.SMTP(ConfiguracaoEmail.SMTP_SERVER, ConfiguracaoEmail.SMTP_PORT)
            server.starttls()
            if ConfiguracaoEmail.EMAIL_PASSWORD:
                server.login(ConfiguracaoEmail.EMAIL_SENDER, ConfiguracaoEmail.EMAIL_PASSWORD)
        else:
            server = smtplib.SMTP_SSL(ConfiguracaoEmail.SMTP_SERVER, ConfiguracaoEmail.SMTP_PORT)
            if ConfiguracaoEmail.EMAIL_PASSWORD:
                server.login(ConfiguracaoEmail.EMAIL_SENDER, ConfiguracaoEmail.EMAIL_PASSWORD)
        
        server.sendmail(ConfiguracaoEmail.EMAIL_SENDER, email_destinatario, msg.as_string())
        server.quit()
        
        print(f"Email enviado com sucesso para {email_destinatario}")
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False


def enviar_email_novo_item(db, item) -> int:
    """Notifica usuários ativos com e-mail quando um novo item entra no catálogo."""
    if not ConfiguracaoEmail.EMAIL_HABILITADO:
        return 0
    try:
        from models import Usuario
        destinatarios = db.query(Usuario).filter(Usuario.ativo.is_(True), Usuario.email.isnot(None)).all()
        enviados = 0
        for usuario in destinatarios:
            corpo = f"""
            <html><body style="font-family:Arial,sans-serif;color:#1e293b">
            <h2>Novo item no almoxarifado</h2>
            <p>Olá {usuario.nome_completo or usuario.username}, um novo item foi adicionado ao inventário.</p>
            <div style="padding:16px;background:#f1f5f9;border-radius:10px">
            <p><strong>Item:</strong> {item.nome}</p><p><strong>Quantidade inicial:</strong> {item.quantidade_total}</p>
            <p><strong>Patrimônio:</strong> {item.patrimonio or 'Não informado'}</p></div>
            <p>Avante Almoxarifado</p></body></html>"""
            if _enviar_smtp(usuario.email, f"Novo item cadastrado: {item.nome}", corpo):
                enviados += 1
        return enviados
    except Exception as e:
        print(f"Erro ao notificar novo item: {e}")
        return 0
