"""Provedor do gerenciador de sessão compartilhado da aplicação."""

from core.session import SessionManager

# Instância única global do SessionManager compartilhada pela aplicação
_session_manager_instance = SessionManager()


def get_session_manager() -> SessionManager:
    """Retorna a instância do gerenciador de sessão ativo."""
    return _session_manager_instance
