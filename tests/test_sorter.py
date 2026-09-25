"""Testes unitários para o módulo de ordenação natural e utilitários funcionais."""

from pathlib import Path

from core.sorter import (
    filter_supported_images,
    is_image_file,
    is_pdf_file,
    natural_sort_key,
    natural_sort_paths,
)


def test_natural_sort_key_order() -> None:
    """Verifica se números em strings são tratados numericamente (1, 2, 10 em vez de 1, 10, 2)."""
    raw_names = ["10.png", "1.png", "2.png", "20.png", "3.png"]
    sorted_names = sorted(raw_names, key=natural_sort_key)
    assert sorted_names == ["1.png", "2.png", "3.png", "10.png", "20.png"]


def test_natural_sort_paths() -> None:
    """Verifica a ordenação de caminhos Path."""
    paths = [Path("slide_12.jpg"), Path("slide_2.jpg"), Path("slide_1.jpg")]
    sorted_paths = natural_sort_paths(paths)
    assert [p.name for p in sorted_paths] == ["slide_1.jpg", "slide_2.jpg", "slide_12.jpg"]


def test_file_type_checks() -> None:
    """Valida a detecção de formatos de imagem e PDF suportados."""
    assert is_image_file("foto.png")
    assert is_image_file("imagem.JPG")
    assert is_image_file("arte.WEBP")
    assert is_pdf_file("documento.pdf")
    assert is_pdf_file("RELATORIO.PDF")

    assert not is_image_file("arquivo.txt")
    assert not is_pdf_file("arquivo.png")


def test_filter_supported_images() -> None:
    """Testa o pipeline funcional do toolz com filtragem e ordenação."""
    items = [
        "10.png",
        "README.md",
        "2.png",
        "doc.pdf",
        "1.png",
        "1.png",  # duplicata proposital
    ]
    res = filter_supported_images(items)
    assert [p.name for p in res] == ["1.png", "2.png", "10.png"]
