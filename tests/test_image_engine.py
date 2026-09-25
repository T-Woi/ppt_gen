"""Testes para o motor de processamento de imagens (Pillow + cache boltons)."""

from pathlib import Path

from PIL import Image

from core.engines.image import (
    clear_image_cache,
    generate_preview_bytes,
    generate_thumbnail_bytes,
    get_image_info,
    load_image_with_orientation_and_rotation,
)


def test_image_inspection_and_cache(tmp_path: Path) -> None:
    """Cria uma imagem de teste e valida inspeção de dimensões e geração de miniatura."""
    test_img_path = tmp_path / "teste_slide.png"
    img = Image.new("RGB", (800, 600), color=(100, 150, 200))
    img.save(test_img_path)

    w, h, fmt = get_image_info(test_img_path)
    assert w == 800
    assert h == 600
    assert fmt.upper() == "PNG"

    # Testa miniatura
    thumb_bytes = generate_thumbnail_bytes(test_img_path, rotation=0, max_size=(200, 200))
    assert len(thumb_bytes) > 0

    # Segunda chamada deve atingir o cache LRU
    cached_bytes = generate_thumbnail_bytes(test_img_path, rotation=0, max_size=(200, 200))
    assert thumb_bytes == cached_bytes

    # Testa preview
    prev_bytes = generate_preview_bytes(test_img_path, rotation=0)
    assert len(prev_bytes) > 0

    # Segunda chamada deve atingir o cache LRU de preview
    cached_prev = generate_preview_bytes(test_img_path, rotation=0)
    assert prev_bytes == cached_prev

    # Limpeza de cache
    clear_image_cache()


def test_image_transparent_and_palette_modes(tmp_path: Path) -> None:
    """Garante suporte a formatos com transparência (RGBA) e paleta (P)."""
    rgba_path = tmp_path / "transparente.png"
    rgba_img = Image.new("RGBA", (200, 150), (255, 0, 0, 128))
    rgba_img.save(rgba_path)

    rgba_thumb = generate_thumbnail_bytes(rgba_path, rotation=90)
    assert len(rgba_thumb) > 0
    rgba_prev = generate_preview_bytes(rgba_path, rotation=90)
    assert len(rgba_prev) > 0

    p_path = tmp_path / "palette.png"
    p_img = Image.new("P", (150, 150))
    p_img.save(p_path)

    p_thumb = generate_thumbnail_bytes(p_path, rotation=0)
    assert len(p_thumb) > 0
    p_prev = generate_preview_bytes(p_path, rotation=0)
    assert len(p_prev) > 0


def test_image_rotation(tmp_path: Path) -> None:
    """Verifica rotação manual de imagem."""
    test_img_path = tmp_path / "retangulo.png"
    img = Image.new("RGB", (400, 200), color=(50, 50, 50))
    img.save(test_img_path)

    # Rotação de 90 graus inverte largura e altura
    rotated_img = load_image_with_orientation_and_rotation(test_img_path, rotation=90)
    assert rotated_img.width == 200
    assert rotated_img.height == 400

    # Rotação de 0 graus
    same_img = load_image_with_orientation_and_rotation(test_img_path, rotation=0)
    assert same_img.width == 400
    assert same_img.height == 200


def test_real_reference_image() -> None:
    """Testa com a imagem real presente na pasta Referencias caso disponível."""
    sample_img = Path("Referencias/CAFÉ DE BOAS-VINDAS/1.png")
    if sample_img.exists():
        w, h, fmt = get_image_info(sample_img)
        assert w > 0
        assert h > 0
        assert fmt.upper() == "PNG"

        thumb = generate_thumbnail_bytes(sample_img)
        assert len(thumb) > 100
