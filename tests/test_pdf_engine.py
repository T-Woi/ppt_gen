"""Testes para o motor de extração e rasterização de PDFs com PyMuPDF."""

from pathlib import Path

import pytest

from core.engines.pdf import (
    clear_pdf_cache,
    generate_pdf_preview_bytes,
    generate_pdf_thumbnail_bytes,
    get_pdf_page_count,
    get_pdf_page_dimensions,
    render_pdf_page_to_image,
)


def test_pdf_engine_full_workflow(sample_pdf: Path) -> None:
    """Valida todas as operações do motor de PDF utilizando o fixture sintético."""
    # 1. Contagem de páginas
    page_count = get_pdf_page_count(sample_pdf)
    assert page_count == 2

    # 2. Dimensões válidas
    w, h = get_pdf_page_dimensions(sample_pdf, 0)
    assert w > 0
    assert h > 0

    # 3. Dimensões com índice inválido
    with pytest.raises(IndexError):
        get_pdf_page_dimensions(sample_pdf, 99)

    with pytest.raises(IndexError):
        get_pdf_page_dimensions(sample_pdf, -1)

    # 4. Renderização para PIL Image (primeira chamada e cache na segunda)
    img1 = render_pdf_page_to_image(sample_pdf, 0, dpi=150, rotation=90)
    assert img1.width > 0
    assert img1.height > 0

    # Segunda chamada (hit no cache de página)
    img2 = render_pdf_page_to_image(sample_pdf, 0, dpi=150, rotation=90)
    assert img2.width == img1.width

    # Renderização com índice inválido
    with pytest.raises(IndexError):
        render_pdf_page_to_image(sample_pdf, 99)

    # 5. Miniatura em bytes (primeira chamada e cache na segunda)
    thumb1 = generate_pdf_thumbnail_bytes(sample_pdf, 0, rotation=0)
    assert len(thumb1) > 0
    assert isinstance(thumb1, bytes)

    thumb2 = generate_pdf_thumbnail_bytes(sample_pdf, 0, rotation=0)
    assert thumb2 == thumb1

    with pytest.raises(IndexError):
        generate_pdf_thumbnail_bytes(sample_pdf, 99)

    # 6. Preview em alta resolução
    prev_bytes = generate_pdf_preview_bytes(sample_pdf, 0, rotation=180)
    assert len(prev_bytes) > 0

    # 7. Limpeza do cache
    clear_pdf_cache()


def test_reference_pdf_file_if_exists() -> None:
    """Verifica que se o PDF de referência opcional existir, executa validações nele."""
    pdf_file = Path("Referencias/A primeira Liderança é sobre Voce!.pdf")
    if pdf_file.exists():
        assert get_pdf_page_count(pdf_file) > 0
