"""Módulo de ordenação natural e processamento funcional com toolz e boltons."""

import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from toolz import itertoolz

SUPPORTED_IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".tiff",
    ".tif",
    ".gif",
}

SUPPORTED_PDF_EXTENSIONS = {".pdf"}


def natural_sort_key(s: str) -> list[Any]:
    """Gera uma chave de ordenação natural (humana), tratando números como inteiros.

    Exemplo: '1.png' < '2.png' < '10.png' (em vez de '10.png' < '2.png').
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", str(s))]


def natural_sort_paths(paths: Iterable[Path | str]) -> list[Path]:
    """Ordena uma coleção de caminhos usando ordenação natural pelo nome do arquivo."""
    path_objs = [Path(p) for p in paths]
    return sorted(path_objs, key=lambda p: natural_sort_key(p.name))


def is_image_file(path: Path | str) -> bool:
    """Verifica se a extensão do arquivo é de imagem suportada."""
    return Path(path).suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS


def is_pdf_file(path: Path | str) -> bool:
    """Verifica se o arquivo é um PDF."""
    return Path(path).suffix.lower() in SUPPORTED_PDF_EXTENSIONS


def filter_supported_images(paths: Iterable[Path | str]) -> list[Path]:
    """Filtra apenas caminhos que são imagens suportadas e ordena de forma natural."""
    img_paths = [Path(p) for p in paths if is_image_file(p)]
    unique_paths = list(itertoolz.unique(img_paths))
    return natural_sort_paths(unique_paths)
