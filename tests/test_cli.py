"""Testes para o analisador de linha de comando (CLI) e ciclo de vida de main.py e __init__.py."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import src
from main import cli_main, launch_webview, parse_arguments


def test_package_init() -> None:
    """Verifica exportações de src/__init__.py."""
    assert src.__version__ == "0.1.0"
    assert "SessionManager" in src.__all__
    assert "build_presentation" in src.__all__
    assert "ppt_gen" in sys.modules


def test_cli_default_arguments(monkeypatch) -> None:
    """Verifica os argumentos padrão quando nenhum parâmetro é passado."""
    monkeypatch.setattr(sys, "argv", ["ppt-gen"])
    args = parse_arguments()
    assert args.input is None


def test_cli_custom_input_long(monkeypatch) -> None:
    """Valida argumento --input passado na CLI."""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "ppt-gen",
            "--input",
            "/caminho/apresentacao.pdf",
        ],
    )
    args = parse_arguments()
    assert args.input == "/caminho/apresentacao.pdf"


def test_cli_custom_input_short(monkeypatch) -> None:
    """Valida argumento -i curto passado na CLI."""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "ppt-gen",
            "-i",
            "C:\\fotos",
        ],
    )
    args = parse_arguments()
    assert args.input == "C:\\fotos"


@patch("main.webview.start")
@patch("main.webview.create_window")
def test_launch_webview_workflow(mock_create_window, mock_start, test_images_dir: Path) -> None:
    """Testa a inicialização do WebView com e sem entrada inicial."""
    mock_window = MagicMock()
    mock_create_window.return_value = mock_window

    # 1. Sem entrada inicial
    launch_webview(None)
    mock_create_window.assert_called_once()
    mock_start.assert_called_once()

    # 2. Com entrada inicial existente (carrega slides)
    mock_create_window.reset_mock()
    mock_start.reset_mock()
    launch_webview(str(test_images_dir))
    mock_create_window.assert_called_once()
    mock_start.assert_called_once()

    # 3. Com entrada inicial inexistente (não quebra)
    mock_create_window.reset_mock()
    mock_start.reset_mock()
    launch_webview("caminho_inexistente_123")
    mock_create_window.assert_called_once()
    mock_start.assert_called_once()


def test_launch_webview_missing_index(monkeypatch, tmp_path: Path) -> None:
    """Verifica se FileNotFoundError é levantado se index.html não existir."""
    fake_web = tmp_path / "fake_web"
    fake_web.mkdir()
    monkeypatch.setattr("main.resolve_web_dir", lambda: fake_web)

    with pytest.raises(FileNotFoundError):
        launch_webview(None)


@patch("main.launch_webview")
@patch("main.parse_arguments")
def test_cli_main(mock_parse, mock_launch) -> None:
    """Valida a execução de cli_main()."""
    mock_parse.return_value = MagicMock(input="test.pdf")
    cli_main()
    mock_launch.assert_called_once_with("test.pdf")
