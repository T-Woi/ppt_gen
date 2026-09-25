"""Testes para validação de modelos de domínio (Attrs), DTOs (Msgspec) e Schemas (Pydantic)."""

import pytest
from pydantic import ValidationError

from core.models import (
    ExportRequest,
    SlideItem,
    SlideItemDto,
    msgspec_json_encoder,
)


def test_domain_slide_item_slots() -> None:
    """Valida o funcionamento dos slots e rotações do SlideItem."""
    item = SlideItem(
        id="item-1",
        source_type="image",
        source_path="/caminho/foto.png",
        title="foto.png",
    )
    assert item.rotation == 0
    assert item.enabled is True

    item.rotate_cw()
    assert item.rotation == 90
    item.rotate_cw()
    assert item.rotation == 180
    item.rotate_ccw()
    assert item.rotation == 90

    item.toggle_enabled()
    assert item.enabled is False


def test_msgspec_dto_encoding_decoding() -> None:
    """Valida a serialização e desserialização ultra-rápida de DTOs via Msgspec."""
    dto = SlideItemDto(
        id="slide-10",
        source_type="image",
        source_path="/tmp/img.png",
        page_index=None,
        title="img.png",
        original_width=1920,
        original_height=1080,
        rotation=0,
        file_size_bytes=10240,
        enabled=True,
        thumbnail_url="/api/thumbnail/slide-10",
        preview_url="/api/preview/slide-10",
    )
    encoded = msgspec_json_encoder.encode(dto)
    assert isinstance(encoded, bytes)

    import msgspec

    decoded = msgspec.json.decode(encoded, type=SlideItemDto)
    assert decoded.id == "slide-10"
    assert decoded.original_width == 1920


def test_pydantic_schemas_validation() -> None:
    """Testa a validação rigorosa de schemas Pydantic para APIs."""
    req = ExportRequest(
        output_dir="/saida",
        filename="Apresentacao",
        aspect_ratio="16:9",
        fit_mode="fit",
    )
    assert req.filename == "Apresentacao"
    assert req.pdf_dpi == 200

    # Validação de fit_mode inválido
    with pytest.raises(ValidationError):
        ExportRequest(
            output_dir="/saida",
            filename="teste",
            fit_mode="invalido",  # type: ignore
        )

    # Validação de DPI fora dos limites
    with pytest.raises(ValidationError):
        ExportRequest(
            output_dir="/saida",
            filename="teste",
            pdf_dpi=50,  # menor que 72
        )
