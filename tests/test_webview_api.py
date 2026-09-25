"""Testes unitários completos para a ponte em memória PyWebViewApi."""

import os
import urllib.parse
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.session import SessionManager
from server.webview_api import PyWebViewApi


def test_webview_api_session_and_presets(session_manager: SessionManager) -> None:
    """Verifica chamada direta de sessão e presets pela API de memória."""
    api = PyWebViewApi(session_manager=session_manager)
    session_data = api.get_session()
    assert "items" in session_data
    assert session_data["total_slides"] == 0

    presets_data = api.get_presets()
    assert "aspect_ratios" in presets_data

    # Teste de getattr e setattr
    assert api.manager is session_manager
    api.window = "fake_window"
    assert api.window == "fake_window"

    with pytest.raises(AttributeError):
        _ = api.propriedade_que_nao_existe


def test_webview_api_workflow_with_images(
    session_manager: SessionManager, test_images_dir: Path
) -> None:
    """Valida o ciclo completo de operações e geração de Data URIs via PyWebViewApi."""
    api = PyWebViewApi(session_manager=session_manager)

    # 1. Carrega pasta
    res = api.load_path(str(test_images_dir.resolve()))
    assert res["total_slides"] == 3
    items = res["items"]
    assert items[0]["thumbnail_url"].startswith("data:image/jpeg;base64,")

    first_id = items[0]["id"]
    second_id = items[1]["id"]
    third_id = items[2]["id"]

    # 2. Testa get_thumbnail e get_preview
    thumb_b64 = api.get_thumbnail(first_id)
    assert thumb_b64.startswith("data:image/jpeg;base64,")
    prev_b64 = api.get_preview(first_id)
    assert prev_b64.startswith("data:image/jpeg;base64,")

    # Item inexistente retorna vazio
    assert api.get_thumbnail("id_inexistente") == ""
    assert api.get_preview("id_inexistente") == ""

    # 3. Rotação, Reordenação, Remoção, Ordenação natural e reversão
    api.rotate(first_id, "cw")
    assert api.get_session()["items"][0]["rotation"] == 90

    api.reorder([second_id, first_id, third_id])
    assert api.get_session()["items"][0]["id"] == second_id

    api.reverse()
    assert api.get_session()["items"][0]["id"] == third_id

    api.sort_natural()
    assert api.get_session()["items"][0]["title"] == "slide_1.png"

    api.remove([third_id])
    assert len(api.get_session()["items"]) == 2

    # 4. Despachante unificado request()
    req_res = api.request("/api/session", "GET")
    assert req_res["ok"] is True
    assert req_res["data"]["total_slides"] == 2

    req_presets = api.request("/api/presets", "GET")
    assert req_presets["ok"] is True

    req_reorder = api.request("/api/reorder", "POST", {"item_ids": [first_id, second_id]})
    assert req_reorder["ok"] is True

    req_remove = api.request("/api/remove", "POST", {"item_ids": [second_id]})
    assert req_remove["ok"] is True

    req_rev = api.request("/api/reverse", "POST")
    assert req_rev["ok"] is True

    req_sort = api.request("/api/sort-natural", "POST")
    assert req_sort["ok"] is True

    req_thumb = api.request(f"/api/thumbnail/{first_id}", "GET")
    assert req_thumb["ok"] is True
    assert req_thumb["data"]["data_url"].startswith("data:")

    req_prev = api.request(f"/api/preview/{first_id}", "GET")
    assert req_prev["ok"] is True
    assert req_prev["data"]["data_url"].startswith("data:")

    # 5. Exportação
    export_payload = {
        "output_dir": str(test_images_dir.parent),
        "filename": "Webview_Teste",  # sem extensão
        "aspect_ratio": "16:9",
        "fit_mode": "fit",
        "bg_color": "#FFFFFF",
        "pdf_dpi": 150,
    }
    exp_res = api.request("/api/export", "POST", export_payload)
    assert exp_res["ok"] is True
    assert exp_res["data"]["success"] is True

    # 6. Limpar sessão
    req_clear = api.request("/api/clear", "POST")
    assert req_clear["ok"] is True
    assert req_clear["data"]["total_slides"] == 0

    # Exportar sessão vazia retorna erro
    exp_empty = api.request("/api/export", "POST", export_payload)
    assert exp_empty["ok"] is False

    # Endpoint inexistente retorna 404
    req_404 = api.request("/api/endpoint-inexistente")
    assert req_404["ok"] is False
    assert req_404["status"] == 404


def test_webview_api_load_path_variations(
    session_manager: SessionManager, test_images_dir: Path
) -> None:
    """Valida as formas aceitas de envio de caminho no endpoint /api/load-path."""
    api = PyWebViewApi(session_manager=session_manager)

    # 1. Via string no body
    r1 = api.request("/api/load-path", "POST", body=str(test_images_dir))
    assert r1["ok"] is True

    # 2. Via query param
    encoded = urllib.parse.quote(str(test_images_dir))
    r2 = api.request(f"/api/load-path?path={encoded}", "POST")
    assert r2["ok"] is True

    # 3. Sem caminho
    r3 = api.request("/api/load-path", "POST", body={})
    assert r3["ok"] is False


def test_webview_api_with_pdf(session_manager: SessionManager, sample_pdf: Path) -> None:
    """Verifica geração de miniaturas e previews para itens de PDF."""
    api = PyWebViewApi(session_manager=session_manager)
    res = api.load_path(str(sample_pdf))
    assert res["total_slides"] == 2
    pdf_item_id = res["items"][0]["id"]

    thumb_b64 = api.get_thumbnail(pdf_item_id)
    assert thumb_b64.startswith("data:image/jpeg;base64,")

    prev_b64 = api.get_preview(pdf_item_id)
    assert prev_b64.startswith("data:image/jpeg;base64,")


def test_webview_api_dialogs_with_window(
    session_manager: SessionManager, test_images_dir: Path, sample_pdf: Path, tmp_path: Path
) -> None:
    """Valida diálogos nativos executados através da janela do PyWebView."""
    api = PyWebViewApi(session_manager=session_manager)

    class MockWindow:
        def __init__(self, return_val=None):
            self.return_val = return_val

        def create_file_dialog(self, *args, **kwargs):
            if isinstance(self.return_val, Exception):
                raise self.return_val
            return self.return_val

    # 1. Selecionar pasta
    api.window = MockWindow([str(test_images_dir)])
    r_folder = api.request("/api/select/folder")
    assert r_folder["ok"] is True
    assert r_folder["data"]["total_slides"] == 3

    # 2. Selecionar PDF
    api.window = MockWindow([str(sample_pdf)])
    r_pdf = api.request("/api/select/pdf")
    assert r_pdf["ok"] is True
    assert r_pdf["data"]["total_slides"] == 2

    # 3. Selecionar imagens
    imgs = [str(p) for p in test_images_dir.glob("*.png")]
    api.window = MockWindow(imgs)
    r_imgs = api.request("/api/select/images")
    assert r_imgs["ok"] is True

    # 4. Selecionar destino para salvar
    target_pptx = tmp_path / "Apresentacao.pptx"
    api.window = MockWindow(str(target_pptx))
    r_dest = api.request("/api/select/destination")
    assert r_dest["ok"] is True
    assert r_dest["data"]["filename"] == "Apresentacao.pptx"

    # 5. Diálogo lançando exceção (fallback seguro)
    api.window = MockWindow(RuntimeError("Erro no diálogo"))
    r_err = api.select_folder()
    assert "items" in r_err


@patch("server.webview_api.ask_folder_async", new_callable=AsyncMock)
@patch("server.webview_api.ask_pdf_async", new_callable=AsyncMock)
@patch("server.webview_api.ask_images_async", new_callable=AsyncMock)
@patch("server.webview_api.ask_save_pptx_async", new_callable=AsyncMock)
def test_webview_api_dialogs_fallback_no_window(
    mock_save,
    mock_imgs,
    mock_pdf,
    mock_folder,
    session_manager: SessionManager,
    test_images_dir: Path,
    sample_pdf: Path,
    tmp_path: Path,
) -> None:
    """Valida o fallback para tkinter quando self._window é None."""
    api = PyWebViewApi(session_manager=session_manager, window=None)

    mock_folder.return_value = str(test_images_dir)
    res_f = api.select_folder()
    assert res_f["total_slides"] == 3

    mock_pdf.return_value = str(sample_pdf)
    res_p = api.select_pdf()
    assert res_p["total_slides"] == 2

    imgs = [str(p) for p in test_images_dir.glob("*.png")]
    mock_imgs.return_value = imgs
    res_i = api.select_images()
    assert res_i["total_slides"] == 3

    mock_save.return_value = str(tmp_path / "Salvo.pptx")
    res_d = api.select_destination()
    assert res_d["filename"] == "Salvo.pptx"


def test_webview_api_open_file_edge_cases(
    session_manager: SessionManager, test_images_dir: Path, monkeypatch
) -> None:
    """Verifica open_file com validações de caminho e multiplataforma."""
    api = PyWebViewApi(session_manager=session_manager)

    # 1. Caminho vazio ou inválido
    with pytest.raises(ValueError):
        api.open_file("")

    with pytest.raises(ValueError):
        api.open_file("null")

    # 2. Execução no macOS (Darwin)
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    with patch("subprocess.run") as mock_sub:
        res = api.open_file(str(test_images_dir))
        assert res["opened"] is True
        mock_sub.assert_called_once()

    # 3. Execução no Linux
    monkeypatch.setattr("platform.system", lambda: "Linux")
    with patch("subprocess.run") as mock_sub:
        res = api.open_file(str(test_images_dir))
        assert res["opened"] is True
        mock_sub.assert_called_once()

    # 4. Execução no Windows (com startfile com sucesso)
    monkeypatch.setattr("platform.system", lambda: "Windows")
    mock_startfile = MagicMock()
    monkeypatch.setattr("os.startfile", mock_startfile, raising=False)
    res = api.open_file(str(test_images_dir))
    assert res["opened"] is True
    mock_startfile.assert_called_once()

    # 5. Execução no Windows (com startfile falhando -> fallback explorer)
    mock_failing_startfile = MagicMock(side_effect=OSError("Erro ao iniciar"))
    monkeypatch.setattr("os.startfile", mock_failing_startfile, raising=False)
    with patch("subprocess.run") as mock_sub:
        res = api.open_file(str(test_images_dir))
        assert res["opened"] is True
        mock_sub.assert_called_once()

    # 6. Execução no Windows (sem startfile -> fallback explorer)
    if hasattr(os, "startfile"):
        monkeypatch.delattr("os.startfile", raising=False)
    with patch("subprocess.run") as mock_sub:
        res = api.open_file(str(test_images_dir))
        assert res["opened"] is True
        mock_sub.assert_called_once()

    # 7. Arquivo inexistente
    with pytest.raises(FileNotFoundError):
        api.open_file(str(test_images_dir / "arquivo_totalmente_inexistente.xyz"))
