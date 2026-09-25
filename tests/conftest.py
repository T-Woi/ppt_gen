"""Configuração e fixtures compartilhadas do Pytest."""

from pathlib import Path

import pytest
from PIL import Image

from core.session import SessionManager


@pytest.fixture
def test_images_dir(tmp_path: Path) -> Path:
    """Cria um diretório temporário contendo imagens de teste com diferentes nomes e orientações."""
    img_dir = tmp_path / "imagens_teste"
    img_dir.mkdir()

    for idx in [1, 2, 10]:
        img = Image.new("RGB", (640, 480), color=(idx * 20, 100, 150))
        img.save(img_dir / f"slide_{idx}.png")

    return img_dir


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Gera um PDF sintético de 2 páginas para testes das rotinas de PDF."""
    import pymupdf

    pdf_path = tmp_path / "teste_documento.pdf"
    doc = pymupdf.open()
    p1 = doc.new_page(width=595, height=842)
    p1.draw_rect([50, 50, 200, 200], color=(1, 0, 0), fill=(0, 1, 0))
    p2 = doc.new_page(width=595, height=842)
    p2.draw_rect([100, 100, 300, 300], color=(0, 0, 1), fill=(1, 1, 0))
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.fixture
def session_manager() -> SessionManager:
    """Retorna uma nova instância isolada de SessionManager para testes unitários."""
    return SessionManager()
