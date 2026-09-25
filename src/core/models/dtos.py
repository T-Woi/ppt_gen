"""Schemas Msgspec para Serialização Ultrarrápida em JSON."""

import msgspec


class SlideItemDto(msgspec.Struct):
    """DTO serializável ultrarrápido para envio ao frontend via JSON."""

    id: str
    source_type: str
    source_path: str
    page_index: int | None
    title: str
    original_width: int
    original_height: int
    rotation: int
    file_size_bytes: int
    enabled: bool
    thumbnail_url: str
    preview_url: str


class SessionManifestDto(msgspec.Struct):
    """Manifesto completo da sessão serializado via msgspec."""

    source_description: str
    suggested_filename: str
    suggested_output_dir: str
    total_slides: int
    items: list[SlideItemDto]


# Codificadores/decodificadores pré-compilados de alto desempenho (10x mais rápidos que stdlib json)
msgspec_json_encoder = msgspec.json.Encoder()
msgspec_json_decoder = msgspec.json.Decoder()
