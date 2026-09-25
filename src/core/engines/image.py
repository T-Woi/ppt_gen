"""Motor de processamento de imagens com Pillow e cache LRU via boltons."""

import io
import threading
from pathlib import Path
from typing import cast

from boltons.cacheutils import LRU
from PIL import Image, ImageOps

_cache_lock = threading.Lock()

# Cache LRU para miniaturas geradas (máximo 500 itens)
_thumbnail_cache: LRU = LRU(max_size=500)
# Cache LRU para previews de tamanho médio (máximo 100 itens)
_preview_cache: LRU = LRU(max_size=100)


def clear_image_cache() -> None:
    """Limpa os caches de miniaturas e previews em memória."""
    with _cache_lock:
        _thumbnail_cache.clear()
        _preview_cache.clear()


def get_image_info(path: Path | str) -> tuple[int, int, str]:
    """Obtém largura, altura e formato da imagem, respeitando a orientação EXIF."""
    path_obj = Path(path)
    with Image.open(path_obj) as raw_img:
        img: Image.Image = ImageOps.exif_transpose(raw_img) or raw_img
        return img.width, img.height, img.format or "PNG"


def load_image_with_orientation_and_rotation(path: Path | str, rotation: int = 0) -> Image.Image:
    """Carrega uma imagem corrigindo orientação EXIF e aplicando rotação manual adicional."""
    with Image.open(path) as raw_img:
        img: Image.Image = (ImageOps.exif_transpose(raw_img) or raw_img).copy()

    if rotation % 360 != 0:
        # Pillow rotate: positivo é sentido anti-horário, portanto usamos -rotation para horário
        img = img.rotate(-rotation, expand=True)

    return img


def generate_thumbnail_bytes(
    path: Path | str,
    rotation: int = 0,
    max_size: tuple[int, int] = (360, 240),
) -> bytes:
    """Gera miniatura em bytes JPEG com cache LRU via boltons e compressão otimizada."""
    cache_key = f"thumb:{path}:{rotation}:{max_size[0]}x{max_size[1]}"
    with _cache_lock:
        cached = _thumbnail_cache.get(cache_key)
    if isinstance(cached, bytes):
        return cached

    with Image.open(path) as raw_img:
        img: Image.Image = ImageOps.exif_transpose(raw_img) or raw_img
        if rotation % 360 != 0:
            img = img.rotate(-rotation, expand=True)

        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
            bg.save(buffer, format="JPEG", quality=85, optimize=True)
        else:
            img.convert("RGB").save(buffer, format="JPEG", quality=85, optimize=True)

        data = buffer.getvalue()
        with _cache_lock:
            _thumbnail_cache[cache_key] = data
        return data


def generate_preview_bytes(
    path: Path | str,
    rotation: int = 0,
    max_size: tuple[int, int] = (1280, 720),
) -> bytes:
    """Gera imagem de visualização em alta resolução para o modal de preview."""
    cache_key = f"prev:{path}:{rotation}:{max_size[0]}x{max_size[1]}"
    with _cache_lock:
        cached = _preview_cache.get(cache_key)
    if isinstance(cached, bytes):
        return cached

    with Image.open(path) as raw_img:
        img: Image.Image = ImageOps.exif_transpose(raw_img) or raw_img
        if rotation % 360 != 0:
            img = img.rotate(-rotation, expand=True)

        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
            bg.save(buffer, format="JPEG", quality=90, optimize=True)
        else:
            img.convert("RGB").save(buffer, format="JPEG", quality=90, optimize=True)

        data = buffer.getvalue()
        with _cache_lock:
            _preview_cache[cache_key] = data
        return cast(bytes, data)
