"""Motores de processamento gráfico, documental e geração do PPT-Gen."""

from core.engines.image import (
    clear_image_cache,
    generate_preview_bytes,
    generate_thumbnail_bytes,
    get_image_info,
    load_image_with_orientation_and_rotation,
)
from core.engines.pdf import (
    clear_pdf_cache,
    generate_pdf_preview_bytes,
    generate_pdf_thumbnail_bytes,
    get_pdf_page_count,
    get_pdf_page_dimensions,
    render_pdf_page_to_image,
)
from core.engines.pptx import (
    build_presentation,
    calculate_slide_geometry,
    parse_hex_color,
)

__all__ = [
    "build_presentation",
    "calculate_slide_geometry",
    "clear_image_cache",
    "clear_pdf_cache",
    "generate_pdf_preview_bytes",
    "generate_pdf_thumbnail_bytes",
    "generate_preview_bytes",
    "generate_thumbnail_bytes",
    "get_image_info",
    "get_pdf_page_count",
    "get_pdf_page_dimensions",
    "load_image_with_orientation_and_rotation",
    "parse_hex_color",
    "render_pdf_page_to_image",
]
