"""Ponte de comunicação em memória para PyWebView (sem abertura de portas ou servidor HTTP)."""

import base64
import os
import platform
import subprocess
import urllib.parse
from pathlib import Path
from typing import Any

import webview

from config import presets
from core.engines.image import (
    generate_preview_bytes,
    generate_thumbnail_bytes,
)
from core.engines.pdf import (
    generate_pdf_preview_bytes,
    generate_pdf_thumbnail_bytes,
)
from core.engines.pptx import build_presentation
from core.session import SessionManager, get_user_documents_dir
from server.dialogs import (
    ask_folder_async,
    ask_images_async,
    ask_pdf_async,
    ask_save_pptx_async,
)

# Compatibilidade com versões modernas do PyWebView (FileDialog) e legadas (*_DIALOG)
_DIALOG_FOLDER = getattr(
    getattr(webview, "FileDialog", None), "FOLDER", getattr(webview, "FOLDER_DIALOG", None)
)
_DIALOG_OPEN = getattr(
    getattr(webview, "FileDialog", None), "OPEN", getattr(webview, "OPEN_DIALOG", None)
)
_DIALOG_SAVE = getattr(
    getattr(webview, "FileDialog", None), "SAVE", getattr(webview, "SAVE_DIALOG", None)
)


class PyWebViewApi:
    """API JS exposta diretamente via IPC em memória pelo PyWebView.

    Não abre nenhum socket TCP nem escuta em qualquer porta de rede.
    A comunicação ocorre 100% em memória através do motor Edge WebView2.
    """

    def __init__(self, session_manager: SessionManager, window: Any = None) -> None:
        self._manager = session_manager
        self._window = window

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ("window", "manager"):
            super().__setattr__("_" + name, value)
            return
        super().__setattr__(name, value)

    def __getattr__(self, name: str) -> Any:
        if name in ("window", "manager"):
            return getattr(self, "_" + name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def _item_to_dict(self, item: Any, include_thumb_base64: bool = True) -> dict[str, Any]:
        """Converte um SlideItem em dicionário com miniatura em Data URI (base64)."""
        thumb_url = f"/api/thumbnail/{item.id}"
        if include_thumb_base64:
            try:
                if item.source_type == "pdf_page":
                    p_idx = item.page_index if item.page_index is not None else 0
                    b = generate_pdf_thumbnail_bytes(
                        item.source_path, p_idx, rotation=item.rotation
                    )
                else:
                    b = generate_thumbnail_bytes(item.source_path, rotation=item.rotation)
                b64 = base64.b64encode(b).decode("ascii")
                thumb_url = f"data:image/jpeg;base64,{b64}"
            except Exception:
                pass

        return {
            "id": item.id,
            "source_type": item.source_type,
            "source_path": item.source_path,
            "page_index": item.page_index,
            "title": item.title,
            "original_width": item.original_width,
            "original_height": item.original_height,
            "rotation": item.rotation,
            "file_size_bytes": item.file_size_bytes,
            "enabled": item.enabled,
            "thumbnail_url": thumb_url,
            "preview_url": f"/api/preview/{item.id}",
        }

    def get_session(self) -> dict[str, Any]:
        """Retorna o estado da sessão com miniaturas prontas em Data URI."""
        items = [self._item_to_dict(it) for it in self._manager.items]
        return {
            "source_description": self._manager.source_description,
            "suggested_filename": self._manager.suggested_filename,
            "suggested_output_dir": self._manager.suggested_output_dir,
            "total_slides": len(items),
            "items": items,
        }

    def get_presets(self) -> dict[str, Any]:
        """Retorna os presets carregados do arquivo YAML."""
        return {
            "defaults": presets.defaults.to_dict(),
            "aspect_ratios": presets.aspect_ratios.to_dict(),
            "fit_modes": presets.fit_modes.to_dict(),
        }

    def load_path(self, path: str, append: bool = False) -> dict[str, Any]:
        """Carrega caminho de pasta ou arquivo PDF."""
        p = Path(path)
        self._manager.load_path(p, append=append)
        return self.get_session()

    def reorder(self, item_ids: list[str]) -> dict[str, Any]:
        """Reordena slides pelos IDs."""
        self._manager.reorder(item_ids)
        return self.get_session()

    def rotate(self, item_id: str, direction: str = "cw") -> dict[str, Any]:
        """Rotaciona um slide específico."""
        self._manager.rotate(item_id, direction)  # type: ignore
        return self.get_session()

    def remove(self, item_ids: list[str]) -> dict[str, Any]:
        """Remove slides selecionados."""
        self._manager.remove(item_ids)
        return self.get_session()

    def clear(self) -> dict[str, Any]:
        """Limpa a sessão inteira."""
        self._manager.clear()
        return self.get_session()

    def sort_natural(self) -> dict[str, Any]:
        """Ordena por ordem natural."""
        self._manager.sort_natural()
        return self.get_session()

    def reverse(self) -> dict[str, Any]:
        """Inverte a ordem dos slides."""
        self._manager.reverse()
        return self.get_session()

    def get_thumbnail(self, item_id: str) -> str:
        """Gera miniatura em Data URI base64."""
        item = self._manager.get_item(item_id)
        if not item:
            return ""
        if item.source_type == "pdf_page":
            page_idx = item.page_index if item.page_index is not None else 0
            b = generate_pdf_thumbnail_bytes(item.source_path, page_idx, rotation=item.rotation)
        else:
            b = generate_thumbnail_bytes(item.source_path, rotation=item.rotation)
        b64 = base64.b64encode(b).decode("ascii")
        return f"data:image/jpeg;base64,{b64}"

    def get_preview(self, item_id: str) -> str:
        """Gera preview de alta definição em Data URI base64."""
        item = self._manager.get_item(item_id)
        if not item:
            return ""
        if item.source_type == "pdf_page":
            page_idx = item.page_index if item.page_index is not None else 0
            b = generate_pdf_preview_bytes(item.source_path, page_idx, rotation=item.rotation)
        else:
            b = generate_preview_bytes(item.source_path, rotation=item.rotation)
        b64 = base64.b64encode(b).decode("ascii")
        return f"data:image/jpeg;base64,{b64}"

    def select_folder(self, append: bool = False) -> dict[str, Any]:
        """Abre diálogo nativo e carrega pasta."""
        initial_dir = self._manager.suggested_output_dir or str(get_user_documents_dir())
        if self._window and hasattr(self._window, "create_file_dialog"):
            try:
                res = self._window.create_file_dialog(
                    _DIALOG_FOLDER,
                    directory=initial_dir,
                )
                if res and len(res) > 0:
                    self._manager.load_folder(Path(res[0]), append=append)
            except Exception as e:
                print(f"[PyWebView] Erro no diálogo de pasta nativo: {e}")
            return self.get_session()

        import asyncio

        folder = asyncio.run(ask_folder_async(initial_dir))
        if folder:
            self._manager.load_folder(Path(folder), append=append)
        return self.get_session()

    def select_pdf(self, append: bool = False) -> dict[str, Any]:
        """Abre diálogo nativo e carrega PDF."""
        initial_dir = self._manager.suggested_output_dir or str(get_user_documents_dir())
        if self._window and hasattr(self._window, "create_file_dialog"):
            try:
                res = self._window.create_file_dialog(
                    _DIALOG_OPEN,
                    directory=initial_dir,
                    file_types=("Arquivos PDF (*.pdf)", "Todos os Arquivos (*.*)"),
                )
                if res and len(res) > 0:
                    self._manager.load_pdf(Path(res[0]), append=append)
            except Exception as e:
                print(f"[PyWebView] Erro no diálogo de PDF nativo: {e}")
            return self.get_session()

        import asyncio

        pdf_file = asyncio.run(ask_pdf_async(initial_dir))
        if pdf_file:
            self._manager.load_pdf(Path(pdf_file), append=append)
        return self.get_session()

    def select_images(self, append: bool = False) -> dict[str, Any]:
        """Abre diálogo nativo e carrega imagens."""
        initial_dir = self._manager.suggested_output_dir or str(get_user_documents_dir())
        if self._window and hasattr(self._window, "create_file_dialog"):
            try:
                res = self._window.create_file_dialog(
                    _DIALOG_OPEN,
                    allow_multiple=True,
                    directory=initial_dir,
                    file_types=(
                        "Imagens Suportadas (*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.tiff)",
                        "Todos os Arquivos (*.*)",
                    ),
                )
                if res:
                    self._manager.load_image_paths([Path(f) for f in res], append=append)
            except Exception as e:
                print(f"[PyWebView] Erro no diálogo de imagens nativo: {e}")
            return self.get_session()

        import asyncio

        files = asyncio.run(ask_images_async(initial_dir))
        if files:
            self._manager.load_image_paths([Path(f) for f in files], append=append)
        return self.get_session()

    def select_destination(self) -> dict[str, Any]:
        """Abre diálogo para salvar apresentação PPTX."""
        initial_dir = self._manager.suggested_output_dir or str(get_user_documents_dir())
        if self._window and hasattr(self._window, "create_file_dialog"):
            try:
                res = self._window.create_file_dialog(
                    _DIALOG_SAVE,
                    directory=initial_dir,
                    save_filename=self._manager.suggested_filename or "Apresentacao.pptx",
                    file_types=("Apresentação PowerPoint (*.pptx)",),
                )
                if res:
                    chosen = res if isinstance(res, str) else res[0]
                    p = Path(chosen)
                    return {
                        "output_dir": str(p.parent),
                        "filename": p.name,
                        "full_path": str(p),
                    }
            except Exception as e:
                print(f"[PyWebView] Erro no diálogo de salvar nativo: {e}")
            return {}

        import asyncio

        chosen = asyncio.run(
            ask_save_pptx_async(
                initial_dir=initial_dir,
                default_filename=self._manager.suggested_filename,
            )
        )

        if chosen:
            p = Path(chosen)
            return {
                "output_dir": str(p.parent),
                "filename": p.name,
                "full_path": str(p),
            }
        return {}

    def export_presentation(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Gera apresentação PowerPoint e salva no disco."""
        items = self._manager.items
        if not items:
            raise ValueError("Nenhum slide disponível para exportação.")

        out_dir = Path(payload["output_dir"])
        filename = payload.get("filename", "Apresentacao.pptx").strip()
        if not filename.lower().endswith(".pptx"):
            filename += ".pptx"

        final_path = out_dir / filename
        saved = build_presentation(
            items=items,
            output_path=final_path,
            aspect_ratio=payload.get("aspect_ratio", "16:9"),
            fit_mode=payload.get("fit_mode", "fit"),
            bg_color=payload.get("bg_color", "#FFFFFF"),
            pdf_dpi=int(payload.get("pdf_dpi", 200)),
        )

        return {
            "success": True,
            "output_path": str(saved.resolve()),
            "output_dir": str(saved.parent.resolve()),
            "filename": saved.name,
            "total_slides": len(items),
            "file_size_bytes": saved.stat().st_size,
            "message": "Apresentação PowerPoint gerada com sucesso!",
        }

    def open_file(self, path: str) -> dict[str, bool]:
        """Abre arquivo ou pasta no explorer do sistema operacional."""
        if not path or str(path).strip() in ("", "None", "null", "undefined"):
            raise ValueError("Caminho não fornecido para abertura.")

        clean_path = str(path).strip().strip('"').strip("'")
        target = Path(clean_path)
        if not target.exists():
            raise FileNotFoundError(f"Arquivo ou pasta não encontrado: {clean_path}")

        resolved = str(target.resolve())
        if platform.system() == "Windows":
            startfile = getattr(os, "startfile", None)
            if callable(startfile):
                try:
                    startfile(resolved)
                except Exception:
                    subprocess.run(["explorer", resolved], check=False)
            else:
                subprocess.run(["explorer", resolved], check=False)
        elif platform.system() == "Darwin":
            subprocess.run(["open", resolved], check=True)  # nosec B603 B607
        else:
            subprocess.run(["xdg-open", resolved], check=True)  # nosec B603 B607
        return {"opened": True}

    def request(self, endpoint: str, method: str = "GET", body: Any = None) -> dict[str, Any]:
        """Roteador unificado para despachar chamadas no formato endpoint REST."""
        clean_endpoint = endpoint.split("?")[0]
        params: dict[str, str] = {}
        if "?" in endpoint:
            for pair in endpoint.split("?")[1].split("&"):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    params[k] = urllib.parse.unquote(v)

        append = params.get("append", "false").lower() == "true"

        try:
            if clean_endpoint == "/api/session":
                return {"ok": True, "status": 200, "data": self.get_session()}
            elif clean_endpoint == "/api/presets":
                return {"ok": True, "status": 200, "data": self.get_presets()}
            elif clean_endpoint == "/api/load-path":
                p = None
                if isinstance(body, dict):
                    p = body.get("path")
                elif isinstance(body, str) and body.strip() and body != "None":
                    p = body.strip()
                if not p and "path" in params:
                    p = params["path"]
                if not p:
                    raise ValueError("Caminho não fornecido para carregamento.")
                return {"ok": True, "status": 200, "data": self.load_path(p, append=append)}
            elif clean_endpoint == "/api/reorder":
                ids = body.get("item_ids", []) if isinstance(body, dict) else list(body)
                return {"ok": True, "status": 200, "data": self.reorder(ids)}
            elif clean_endpoint == "/api/rotate":
                item_id = body.get("item_id")
                direction = body.get("direction", "cw")
                return {"ok": True, "status": 200, "data": self.rotate(item_id, direction)}
            elif clean_endpoint == "/api/remove":
                ids = body.get("item_ids", [])
                return {"ok": True, "status": 200, "data": self.remove(ids)}
            elif clean_endpoint == "/api/clear":
                return {"ok": True, "status": 200, "data": self.clear()}
            elif clean_endpoint == "/api/sort-natural":
                return {"ok": True, "status": 200, "data": self.sort_natural()}
            elif clean_endpoint == "/api/reverse":
                return {"ok": True, "status": 200, "data": self.reverse()}
            elif clean_endpoint == "/api/select/folder":
                return {"ok": True, "status": 200, "data": self.select_folder(append=append)}
            elif clean_endpoint == "/api/select/pdf":
                return {"ok": True, "status": 200, "data": self.select_pdf(append=append)}
            elif clean_endpoint == "/api/select/images":
                return {"ok": True, "status": 200, "data": self.select_images(append=append)}
            elif clean_endpoint == "/api/select/destination":
                return {"ok": True, "status": 200, "data": self.select_destination()}
            elif clean_endpoint == "/api/export":
                return {"ok": True, "status": 200, "data": self.export_presentation(body or {})}
            elif clean_endpoint == "/api/open-file":
                p = None
                if isinstance(body, dict):
                    p = body.get("path")
                elif isinstance(body, str) and body.strip() and body != "None":
                    p = body.strip()
                if not p and "path" in params:
                    p = params["path"]
                if not p:
                    raise ValueError("Caminho não fornecido para abertura.")
                return {"ok": True, "status": 200, "data": self.open_file(p)}
            elif clean_endpoint.startswith("/api/preview/"):
                item_id = clean_endpoint.split("/api/preview/")[1]
                data_url = self.get_preview(item_id)
                return {"ok": True, "status": 200, "data": {"data_url": data_url}}
            elif clean_endpoint.startswith("/api/thumbnail/"):
                item_id = clean_endpoint.split("/api/thumbnail/")[1]
                data_url = self.get_thumbnail(item_id)
                return {"ok": True, "status": 200, "data": {"data_url": data_url}}
            else:
                return {
                    "ok": False,
                    "status": 404,
                    "error": f"Endpoint não encontrado: {clean_endpoint}",
                }
        except Exception as e:
            return {"ok": False, "status": 500, "error": str(e)}
