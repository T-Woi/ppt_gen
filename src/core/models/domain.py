"""Modelos de Domínio com Attrs (__slots__ = True para alta eficiência e baixo consumo de memória)."""

from typing import Literal

import attrs


@attrs.define(slots=True)
class SlideGeometry:
    """Geometria calculada para posicionamento de uma imagem dentro de um slide."""

    slide_width_inches: float
    slide_height_inches: float
    image_width: int
    image_height: int
    left_inches: float
    top_inches: float
    render_width_inches: float
    render_height_inches: float


@attrs.define(slots=True)
class SlideItem:
    """Representação interna de um item/slide com slots leves."""

    id: str
    source_type: Literal["image", "pdf_page"]
    source_path: str
    page_index: int | None = None
    title: str = ""
    original_width: int = 0
    original_height: int = 0
    rotation: int = 0  # 0, 90, 180, 270 graus
    file_size_bytes: int = 0
    enabled: bool = True

    def rotate_cw(self) -> None:
        """Rotaciona 90 graus no sentido horário."""
        self.rotation = (self.rotation + 90) % 360

    def rotate_ccw(self) -> None:
        """Rotaciona 90 graus no sentido anti-horário."""
        self.rotation = (self.rotation - 90) % 360

    def toggle_enabled(self) -> bool:
        """Alterna a visibilidade do slide e retorna o novo estado."""
        self.enabled = not self.enabled
        return self.enabled


@attrs.define(slots=True)
class ConversionJob:
    """Representa uma sessão/tarefa completa de conversão."""

    job_id: str
    source_description: str
    suggested_filename: str
    suggested_output_dir: str
    items: list[SlideItem] = attrs.field(factory=list)
