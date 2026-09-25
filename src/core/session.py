"""Gerenciador central de sessão e manipulação de slides do PPT-Gen Studio."""

import threading
import uuid
from pathlib import Path
from typing import Literal

from core.engines.image import get_image_info
from core.engines.pdf import get_pdf_page_count, get_pdf_page_dimensions
from core.models.domain import ConversionJob, SlideItem
from core.models.dtos import (
    SessionManifestDto,
    SlideItemDto,
    msgspec_json_encoder,
)
from core.sorter import filter_supported_images, natural_sort_key


def get_user_documents_dir() -> Path:
    """Retorna o caminho padrão da pasta de Documentos do usuário no Windows."""
    docs = Path.home() / "Documents"
    if docs.exists():
        return docs
    docs_pt = Path.home() / "Documentos"
    if docs_pt.exists():
        return docs_pt
    onedrive_docs = Path.home() / "OneDrive" / "Documents"
    if onedrive_docs.exists():
        return onedrive_docs
    return Path.home()


class SessionManager:
    """Gerenciador seguro e orientado a objetos para o estado de conversão da aplicação.

    Protegido com lock reentrante (RLock) para garantir consistência em requisições
    concorrentes de frontend (como carregamento simultâneo de miniaturas, rotações e reordenações).
    """

    def __init__(self, initial_job: ConversionJob | None = None) -> None:
        self._lock = threading.RLock()
        self._job = initial_job or ConversionJob(
            job_id=str(uuid.uuid4()),
            source_description="Nenhum arquivo carregado",
            suggested_filename="Apresentacao.pptx",
            suggested_output_dir=str(get_user_documents_dir()),
            items=[],
        )

    @property
    def job(self) -> ConversionJob:
        """Acesso somente-leitura ao objeto ConversionJob subjacente."""
        return self._job

    @property
    def items(self) -> list[SlideItem]:
        """Retorna uma cópia rasa da lista de itens para evitar mutações externas descontroladas."""
        with self._lock:
            return list(self._job.items)

    @property
    def source_description(self) -> str:
        with self._lock:
            return str(self._job.source_description)

    @property
    def suggested_filename(self) -> str:
        with self._lock:
            return str(self._job.suggested_filename)

    @suggested_filename.setter
    def suggested_filename(self, value: str) -> None:
        with self._lock:
            self._job.suggested_filename = value

    @property
    def suggested_output_dir(self) -> str:
        with self._lock:
            return str(self._job.suggested_output_dir)

    @suggested_output_dir.setter
    def suggested_output_dir(self, value: str) -> None:
        with self._lock:
            self._job.suggested_output_dir = value

    def get_item(self, item_id: str) -> SlideItem | None:
        """Busca um item específico pelo ID."""
        with self._lock:
            return next((it for it in self._job.items if it.id == item_id), None)

    def build_manifest(self) -> SessionManifestDto:
        """Monta o DTO de manifesto leve para transmissão rápida via JSON."""
        with self._lock:
            dtos: list[SlideItemDto] = []
            for item in self._job.items:
                dtos.append(
                    SlideItemDto(
                        id=item.id,
                        source_type=item.source_type,
                        source_path=item.source_path,
                        page_index=item.page_index,
                        title=item.title,
                        original_width=item.original_width,
                        original_height=item.original_height,
                        rotation=item.rotation,
                        file_size_bytes=item.file_size_bytes,
                        enabled=item.enabled,
                        thumbnail_url=f"/api/thumbnail/{item.id}",
                        preview_url=f"/api/preview/{item.id}",
                    )
                )
            return SessionManifestDto(
                source_description=self._job.source_description,
                suggested_filename=self._job.suggested_filename,
                suggested_output_dir=self._job.suggested_output_dir,
                total_slides=len(self._job.items),
                items=dtos,
            )

    def get_manifest_bytes(self) -> bytes:
        """Serializa o manifesto diretamente em bytes JSON com msgspec de alta velocidade."""
        manifest = self.build_manifest()
        return bytes(msgspec_json_encoder.encode(manifest))

    def load_folder(self, folder_path: Path, append: bool = False) -> int:
        """Varre e carrega todas as imagens suportadas de uma pasta."""
        if not folder_path.exists() or not folder_path.is_dir():
            raise ValueError(f"Pasta inválida ou inexistente: '{folder_path}'")

        image_paths = filter_supported_images(folder_path.iterdir())
        if not image_paths:
            raise ValueError(f"Nenhuma imagem suportada encontrada na pasta '{folder_path.name}'.")

        with self._lock:
            if not append:
                self._job.items.clear()
                self._job.source_description = f"Pasta: {folder_path.name}"
                self._job.suggested_filename = f"{folder_path.name}.pptx"
                if not self._job.suggested_output_dir:
                    self._job.suggested_output_dir = str(get_user_documents_dir())

            for img_path in image_paths:
                try:
                    w, h, _ = get_image_info(img_path)
                    size = img_path.stat().st_size
                except Exception:
                    w, h, size = 0, 0, 0

                item = SlideItem(
                    id=str(uuid.uuid4()),
                    source_type="image",
                    source_path=str(img_path.resolve()),
                    title=img_path.name,
                    original_width=w,
                    original_height=h,
                    rotation=0,
                    file_size_bytes=size,
                )
                self._job.items.append(item)

        return len(image_paths)

    def load_pdf(self, pdf_path: Path, append: bool = False) -> int:
        """Abre um arquivo PDF e extrai cada página como um slide."""
        if not pdf_path.exists() or not pdf_path.is_file():
            raise ValueError(f"Arquivo PDF não encontrado: '{pdf_path}'")

        total_pages = get_pdf_page_count(pdf_path)
        if total_pages == 0:
            raise ValueError("O PDF fornecido não possui páginas.")

        with self._lock:
            if not append:
                self._job.items.clear()
                self._job.source_description = f"PDF: {pdf_path.name}"
                self._job.suggested_filename = f"{pdf_path.stem}.pptx"
                if not self._job.suggested_output_dir:
                    self._job.suggested_output_dir = str(get_user_documents_dir())

            file_size = pdf_path.stat().st_size

            for page_idx in range(total_pages):
                try:
                    w_pt, h_pt = get_pdf_page_dimensions(pdf_path, page_idx)
                    w_px = int(w_pt * 200 / 72)
                    h_px = int(h_pt * 200 / 72)
                except Exception:
                    w_px, h_px = 1920, 1080

                item = SlideItem(
                    id=str(uuid.uuid4()),
                    source_type="pdf_page",
                    source_path=str(pdf_path.resolve()),
                    page_index=page_idx,
                    title=f"Página {page_idx + 1}",
                    original_width=w_px,
                    original_height=h_px,
                    rotation=0,
                    file_size_bytes=file_size,
                )
                self._job.items.append(item)

        return int(total_pages)

    def load_image_paths(
        self,
        paths: list[Path],
        append: bool = False,
        source_description: str | None = None,
    ) -> int:
        """Adiciona uma lista avulsa de imagens suportadas."""
        sorted_files = filter_supported_images(paths)
        if not sorted_files:
            return 0

        with self._lock:
            if not append:
                self._job.items.clear()
                first_parent = sorted_files[0].parent
                self._job.source_description = (
                    source_description or f"{len(sorted_files)} Imagens selecionadas"
                )
                self._job.suggested_filename = f"{first_parent.name}.pptx"
                if not self._job.suggested_output_dir:
                    self._job.suggested_output_dir = str(get_user_documents_dir())

            for img_path in sorted_files:
                try:
                    w, h, _ = get_image_info(img_path)
                    size = img_path.stat().st_size
                except Exception:
                    w, h, size = 0, 0, 0

                item = SlideItem(
                    id=str(uuid.uuid4()),
                    source_type="image",
                    source_path=str(img_path.resolve()),
                    title=img_path.name,
                    original_width=w,
                    original_height=h,
                    rotation=0,
                    file_size_bytes=size,
                )
                self._job.items.append(item)

        return len(sorted_files)

    def load_path(self, target_path: Path, append: bool = False) -> int:
        """Identifica dinamicamente se o caminho é pasta, PDF ou imagem e carrega adequadamente."""
        if not target_path.exists():
            raise FileNotFoundError(f"Caminho especificado não existe: {target_path}")

        if target_path.is_dir():
            return self.load_folder(target_path, append=append)
        elif target_path.suffix.lower() == ".pdf":
            return self.load_pdf(target_path, append=append)
        elif target_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}:
            return self.load_folder(target_path.parent, append=append)
        else:
            raise ValueError(f"Formato ou tipo de caminho não suportado: {target_path}")

    def reorder(self, item_ids: list[str]) -> None:
        """Reorganiza a lista de itens com base na ordem dos IDs passados."""
        with self._lock:
            item_map = {item.id: item for item in self._job.items}
            new_items: list[SlideItem] = []
            for item_id in item_ids:
                if item_id in item_map:
                    new_items.append(item_map[item_id])

            # Preserva itens que não foram mencionados no final
            remaining = [it for it in self._job.items if it.id not in item_ids]
            new_items.extend(remaining)
            self._job.items = new_items

    def rotate(self, item_id: str, direction: Literal["cw", "ccw"] = "cw") -> bool:
        """Rotaciona um slide específico por 90 graus."""
        with self._lock:
            item = self.get_item(item_id)
            if not item:
                return False
            if direction == "cw":
                item.rotate_cw()
            else:
                item.rotate_ccw()
            return True

    def remove(self, item_ids: list[str]) -> int:
        """Remove os itens selecionados da sessão."""
        with self._lock:
            to_remove = set(item_ids)
            initial_count = len(self._job.items)
            self._job.items = [it for it in self._job.items if it.id not in to_remove]
            return initial_count - len(self._job.items)

    def clear(self) -> None:
        """Limpa todos os itens da sessão."""
        with self._lock:
            self._job.items.clear()
            self._job.source_description = "Nenhum arquivo carregado"

    def sort_natural(self) -> None:
        """Ordena os itens da sessão por ordem natural do título."""
        with self._lock:
            self._job.items.sort(key=lambda it: natural_sort_key(it.title))

    def reverse(self) -> None:
        """Inverte a ordem dos itens da sessão."""
        with self._lock:
            self._job.items.reverse()
