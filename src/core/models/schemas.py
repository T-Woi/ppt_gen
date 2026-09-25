"""Modelos Pydantic para Validação de Entrada e Respostas da API."""

from typing import Literal

from pydantic import BaseModel, Field


class PathInputRequest(BaseModel):
    """Requisição para carregar arquivo ou pasta diretamente."""

    path: str = Field(..., description="Caminho absoluto ou relativo da pasta ou arquivo")


class ReorderRequest(BaseModel):
    """Requisição para reordenar os slides da sessão atual."""

    item_ids: list[str] = Field(..., description="Lista ordenada de IDs dos slides")


class RotateRequest(BaseModel):
    """Requisição para rotacionar um slide específico."""

    item_id: str
    direction: Literal["cw", "ccw"] = "cw"


class RemoveItemsRequest(BaseModel):
    """Requisição para remover um ou mais slides."""

    item_ids: list[str]


class ExportRequest(BaseModel):
    """Requisição para gerar e salvar a apresentação PPTX."""

    output_dir: str = Field(..., description="Diretório de destino onde salvar o PPTX")
    filename: str = Field(..., description="Nome do arquivo de saída (com ou sem extensão .pptx)")
    aspect_ratio: str = Field(
        default="16:9", description="Proporção do slide ('16:9', '4:3', etc.)"
    )
    fit_mode: Literal["fit", "fill", "stretch"] = Field(
        default="fit", description="Modo de encaixe da imagem no slide"
    )
    bg_color: str = Field(
        default="#FFFFFF", description="Cor de fundo em hexadecimal (ex: #FFFFFF)"
    )
    pdf_dpi: int = Field(default=200, ge=72, le=600, description="DPI de renderização para PDFs")


class ExportResponse(BaseModel):
    """Resposta com o resultado da exportação."""

    success: bool
    output_path: str
    output_dir: str = Field(default="", description="Diretório onde a apresentação foi salva")
    filename: str
    total_slides: int
    file_size_bytes: int
    message: str


class OpenFileRequest(BaseModel):
    """Requisição para abrir arquivo ou pasta no gerenciador do sistema."""

    path: str = Field(..., description="Caminho do arquivo ou pasta a ser aberto")
