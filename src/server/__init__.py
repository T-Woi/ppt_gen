"""Módulo de integração e interface IPC para PyWebView."""

from server.deps import get_session_manager
from server.webview_api import PyWebViewApi

__all__ = ["PyWebViewApi", "get_session_manager"]
