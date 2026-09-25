"""Módulo unificado de modelos do PPT-Gen Studio.

Exporta modelos de domínio com slots (attrs), DTOs ultrarrápidos (msgspec)
e schemas de validação de requisições/respostas (pydantic).
"""

from core.models.domain import ConversionJob, SlideGeometry, SlideItem
from core.models.dtos import (
    SessionManifestDto,
    SlideItemDto,
    msgspec_json_decoder,
    msgspec_json_encoder,
)
from core.models.schemas import (
    ExportRequest,
    ExportResponse,
    PathInputRequest,
    RemoveItemsRequest,
    ReorderRequest,
    RotateRequest,
)

__all__ = [
    "ConversionJob",
    "ExportRequest",
    "ExportResponse",
    "PathInputRequest",
    "RemoveItemsRequest",
    "ReorderRequest",
    "RotateRequest",
    "SessionManifestDto",
    "SlideGeometry",
    "SlideItem",
    "SlideItemDto",
    "msgspec_json_decoder",
    "msgspec_json_encoder",
]
