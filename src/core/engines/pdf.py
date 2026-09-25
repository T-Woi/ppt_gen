"""Motor de processamento de PDFs utilizando PyMuPDF (fitz) com cache LRU."""

import io
import threading
from pathlib import Path

import pymupdf
from boltons.cacheutils import LRU
from PIL import Image

_pdf_cache_lock = threading.Lock()

# Cache para páginas rasterizadas de PDF (máximo 200 páginas em memória)
_pdf_page_cache = LRU(max_size=200)
_pdf_thumb_cache = LRU(max_size=300)


def clear_pdf_cache() -> None:
    """Limpa caches de rasterização de PDF."""
    with _pdf_cache_lock:
        _pdf_page_cache.clear()
        _pdf_thumb_cache.clear()


def get_pdf_page_count(pdf_path: Path | str) -> int:
    """Retorna o número total de páginas do arquivo PDF."""
    with pymupdf.open(str(pdf_path)) as doc:
        return len(doc)


def get_pdf_page_dimensions(pdf_path: Path | str, page_index: int = 0) -> tuple[int, int]:
    """Retorna a largura e altura em pontos (pt) da página especificada."""
    with pymupdf.open(str(pdf_path)) as doc:
        if page_index < 0 or page_index >= len(doc):
            raise IndexError(f"Índice de página {page_index} fora dos limites (total: {len(doc)})")
        page = doc[page_index]
        rect = page.rect
        return int(rect.width), int(rect.height)


def render_pdf_page_to_image(
    pdf_path: Path | str,
    page_index: int,
    dpi: int = 200,
    rotation: int = 0,
) -> Image.Image:
    """Renderiza uma página do PDF para um objeto PIL Image com alta resolução e rotação opcional."""
    cache_key = f"page:{pdf_path}:{page_index}:{dpi}:{rotation}"
    with _pdf_cache_lock:
        cached = _pdf_page_cache.get(cache_key)
    if cached is not None:
        return Image.open(io.BytesIO(cached))

    with pymupdf.open(str(pdf_path)) as doc:
        if page_index < 0 or page_index >= len(doc):
            raise IndexError(f"Página {page_index} inválida para {pdf_path}")

        page = doc[page_index]
        combined_rotation = (page.rotation + rotation) % 360

        # Matrix de escala baseada no DPI (72 DPI padrão do PDF)
        zoom = dpi / 72.0
        mat = pymupdf.Matrix(zoom, zoom).prerotate(combined_rotation)

        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_bytes = pix.tobytes("png")

        with _pdf_cache_lock:
            _pdf_page_cache[cache_key] = img_bytes
        return Image.open(io.BytesIO(img_bytes))


def generate_pdf_thumbnail_bytes(
    pdf_path: Path | str,
    page_index: int,
    rotation: int = 0,
    max_size: tuple[int, int] = (360, 240),
) -> bytes:
    """Gera miniatura rápida de uma página do PDF em JPEG."""
    cache_key = f"pdf_thumb:{pdf_path}:{page_index}:{rotation}:{max_size[0]}x{max_size[1]}"
    with _pdf_cache_lock:
        cached = _pdf_thumb_cache.get(cache_key)
    if isinstance(cached, bytes):
        return cached

    # Renderiza com DPI leve (96 DPI) para velocidade
    with pymupdf.open(str(pdf_path)) as doc:
        if page_index < 0 or page_index >= len(doc):
            raise IndexError(f"Página {page_index} inválida para {pdf_path}")

        page = doc[page_index]
        combined_rotation = (page.rotation + rotation) % 360
        zoom = 96.0 / 72.0
        mat = pymupdf.Matrix(zoom, zoom).prerotate(combined_rotation)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        raw_bytes = pix.tobytes("png")

    with Image.open(io.BytesIO(raw_bytes)) as img:
        img.thumbnail(max_size, Image.Resampling.BILINEAR)
        buffer = io.BytesIO()
        img.convert("RGB").save(buffer, format="JPEG", quality=80, optimize=True)
        data = buffer.getvalue()
        with _pdf_cache_lock:
            _pdf_thumb_cache[cache_key] = data
        return data


def generate_pdf_preview_bytes(
    pdf_path: Path | str,
    page_index: int,
    rotation: int = 0,
) -> bytes:
    """Gera visualização de página de PDF em boa resolução para o modal."""
    img = render_pdf_page_to_image(pdf_path, page_index, dpi=150, rotation=rotation)
    buffer = io.BytesIO()
    img.convert("RGB").save(buffer, format="JPEG", quality=88, optimize=True)
    return buffer.getvalue()
