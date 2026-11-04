"""
Tarefas agendadas para verificar empréstimos atrasados e enviar emails de notificação.
"""
import os
from datetime import datetime, UTC, timedelta
import sqlalchemy as sa
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from models import Emprestimo, Usuario
from email_service import enviar_email_lembrete_devolucao, enviar_email_atraso_devolucao


scheduler = BackgroundScheduler()


def _agora_naive_utc() -> datetime:
    """Datetime atual em UTC, sem tzinfo."""
    return datetime.now(UTC).replace(tzinfo=None)


def verificar_e_enviar_alertas_devolucao(db: Session) -> None:
    """
    Verifica empréstimos e envia emails:
    1. Lembrete: 1 dia antes da devolução
    2. Alerta: empréstimo atrasado
    """
    agora = _agora_naive_utc()
    
    try:
        # --- LEMBRETE: 1 dia antes ---
        # Empréstimos que vencem em 24 horas (entre agora e agora + 24h)
        amanha = agora + timedelta(days=1)
        
        emprestimos_para_lembrar = (
            db.query(Emprestimo)
            .filter(
                Emprestimo.status == "EM_ANDAMENTO",
                Emprestimo.data_devolucao_prevista >= agora,
                Emprestimo.data_devolucao_prevista <= amanha,
                Emprestimo.emails_enviados == False,  # Ainda não enviamos lembrete
                Emprestimo.usuario_id.isnot(None),
            )
            .all()
        )
        
        for emp in emprestimos_para_lembrar:
            if emp.usuario and emp.usuario.email:
                sucesso = enviar_email_lembrete_devolucao(
                    email_destinatario=emp.usuario.email,
                    nome_usuario=emp.usuario.nome_completo or emp.usuario.username,
                    nome_item=emp.item.nome if emp.item else "(Item removido)",
                    quantidade=emp.quantidade,
                    data_devolucao=emp.data_devolucao_prevista,
                )
                
                if sucesso:
                    emp.emails_enviados = True
                    db.commit()
        
        # --- ALERTA: ATRASO ---
        # Empréstimos que passaram da data limite de tolerância.
        # Diferente do lembrete (uma única vez), o alerta de atraso se
        # repete enquanto o item não volta — mas no máximo UMA VEZ POR DIA.
        # O scheduler roda de hora em hora; sem o filtro por
        # `ultimo_alerta_atraso`, a mesma pessoa receberia 24 e-mails por
        # dia até devolver o item.
        limite_reenvio = agora - timedelta(hours=24)

        emprestimos_atrasados = (
            db.query(Emprestimo)
            .filter(
                Emprestimo.status == "EM_ANDAMENTO",
                Emprestimo.data_limite_tolerancia < agora,  # Passou da tolerância
                Emprestimo.usuario_id.isnot(None),
                sa.or_(
                    Emprestimo.ultimo_alerta_atraso.is_(None),
                    Emprestimo.ultimo_alerta_atraso <= limite_reenvio,
                ),
            )
            .all()
        )

        for emp in emprestimos_atrasados:
            if emp.usuario and emp.usuario.email:
                dias_atrasado = (agora - emp.data_limite_tolerancia).days

                sucesso = enviar_email_atraso_devolucao(
                    email_destinatario=emp.usuario.email,
                    nome_usuario=emp.usuario.nome_completo or emp.usuario.username,
                    nome_item=emp.item.nome if emp.item else "(Item removido)",
                    quantidade=emp.quantidade,
                    data_devolucao_prevista=emp.data_devolucao_prevista,
                    dias_atrasado=dias_atrasado,
                )

                # Só marca como enviado se realmente saiu — assim uma falha
                # temporária de SMTP é reprocessada na próxima execução, em
                # vez de o aviso ser silenciosamente perdido.
                if sucesso:
                    emp.ultimo_alerta_atraso = agora
                    db.commit()
        
        print(f"[{agora}] Verificação de alertas de devolução concluída")
    
    except Exception as e:
        print(f"Erro ao verificar alertas de devolução: {e}")


def iniciar_scheduler(db_session_factory):
    """
    Inicia o agendador de tarefas de background.
    
    Args:
        db_session_factory: Factory de sessões do SQLAlchemy
    """
    if not scheduler.running:
        # Verificar alertas a cada 1 hora
        def task_com_db():
            db = db_session_factory()
            try:
                verificar_e_enviar_alertas_devolucao(db)
            finally:
                db.close()
        
        scheduler.add_job(
            task_com_db,
            trigger=IntervalTrigger(minutes=60),
            id="verificar_alertas_devolucao",
            name="Verificar alertas de devolução",
            replace_existing=True,
        )
        
        scheduler.start()
        print("✅ Agendador de tarefas iniciado")


def parar_scheduler():
    """Para o agendador de tarefas."""
    if scheduler.running:
        scheduler.shutdown()
        print("✅ Agendador de tarefas parado")
