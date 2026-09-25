"""Testes para server/deps.py e diálogos nativos em server/dialogs.py."""

import asyncio
from unittest.mock import MagicMock, patch

from server.deps import get_session_manager
from server.dialogs import (
    _run_native_folder_dialog,
    _run_native_images_dialog,
    _run_native_pdf_dialog,
    _run_native_save_pptx_dialog,
    ask_folder_async,
    ask_images_async,
    ask_pdf_async,
    ask_save_pptx_async,
)


def test_deps_get_session_manager() -> None:
    """Verifica se o singleton do SessionManager é retornado corretamente."""
    mgr = get_session_manager()
    assert mgr is not None
    assert get_session_manager() is mgr


@patch("server.dialogs.tk.Tk")
@patch("server.dialogs.filedialog.askdirectory")
def test_folder_dialog(mock_askdir, mock_tk) -> None:
    """Testa diálogo de pasta retornando caminho e cancelado."""
    mock_tk_instance = MagicMock()
    mock_tk.return_value = mock_tk_instance

    # Selecionou pasta
    mock_askdir.return_value = "C:/Imagens"
    res = _run_native_folder_dialog("C:/")
    assert res == "C:/Imagens"
    mock_tk_instance.destroy.assert_called()

    # Cancelou
    mock_askdir.return_value = ""
    res_cancel = _run_native_folder_dialog()
    assert res_cancel is None


@patch("server.dialogs.tk.Tk")
@patch("server.dialogs.filedialog.askopenfilename")
def test_pdf_dialog(mock_askfile, mock_tk) -> None:
    """Testa diálogo de PDF retornando caminho e cancelado."""
    mock_tk.return_value = MagicMock()

    # Selecionou PDF
    mock_askfile.return_value = "C:/docs/apresentacao.pdf"
    res = _run_native_pdf_dialog("C:/docs")
    assert res == "C:/docs/apresentacao.pdf"

    # Cancelou
    mock_askfile.return_value = ""
    assert _run_native_pdf_dialog() is None


@patch("server.dialogs.tk.Tk")
@patch("server.dialogs.filedialog.askopenfilenames")
def test_images_dialog(mock_askfiles, mock_tk) -> None:
    """Testa diálogo de múltiplas imagens retornando arquivos e cancelado."""
    mock_tk.return_value = MagicMock()

    # Selecionou imagens
    mock_askfiles.return_value = ("C:/img1.png", "C:/img2.jpg")
    res = _run_native_images_dialog("C:/")
    assert res == ["C:/img1.png", "C:/img2.jpg"]

    # Cancelou
    mock_askfiles.return_value = ()
    assert _run_native_images_dialog() == []


@patch("server.dialogs.tk.Tk")
@patch("server.dialogs.filedialog.asksaveasfilename")
def test_save_pptx_dialog(mock_asksave, mock_tk) -> None:
    """Testa diálogo para salvar PPTX com sucesso e cancelado."""
    mock_tk.return_value = MagicMock()

    # Selecionou destino
    mock_asksave.return_value = "C:/docs/Final.pptx"
    res = _run_native_save_pptx_dialog("C:/docs", "Final.pptx")
    assert res == "C:/docs/Final.pptx"

    # Cancelou
    mock_asksave.return_value = ""
    assert _run_native_save_pptx_dialog() is None


@patch("server.dialogs._run_native_folder_dialog", return_value="C:/Folder")
@patch("server.dialogs._run_native_pdf_dialog", return_value="C:/Doc.pdf")
@patch("server.dialogs._run_native_images_dialog", return_value=["C:/1.png"])
@patch("server.dialogs._run_native_save_pptx_dialog", return_value="C:/Salvo.pptx")
def test_async_dialog_wrappers(mock_save, mock_imgs, mock_pdf, mock_folder) -> None:
    """Testa os wrappers assíncronos que executam via asyncio.to_thread."""
    assert asyncio.run(ask_folder_async()) == "C:/Folder"
    assert asyncio.run(ask_pdf_async()) == "C:/Doc.pdf"
    assert asyncio.run(ask_images_async()) == ["C:/1.png"]
    assert asyncio.run(ask_save_pptx_async()) == "C:/Salvo.pptx"
