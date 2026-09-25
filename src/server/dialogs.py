"""Diálogos nativos do sistema operacional para seleção de arquivos e pastas."""

import asyncio
import tkinter as tk
from tkinter import filedialog

from core.session import get_user_documents_dir


def _run_native_folder_dialog(initial_dir: str | None = None) -> str | None:
    """Abre o diálogo nativo do Windows para seleção de pasta."""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        folder = filedialog.askdirectory(
            parent=root,
            title="Selecione a Pasta de Imagens",
            initialdir=initial_dir or str(get_user_documents_dir()),
        )
        return folder if folder else None
    finally:
        root.destroy()


def _run_native_pdf_dialog(initial_dir: str | None = None) -> str | None:
    """Abre o diálogo nativo para seleção de arquivo PDF."""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        file_path = filedialog.askopenfilename(
            parent=root,
            title="Selecione o Arquivo PDF",
            initialdir=initial_dir or str(get_user_documents_dir()),
            filetypes=[("Arquivos PDF (*.pdf)", "*.pdf"), ("Todos os Arquivos", "*.*")],
        )
        return file_path if file_path else None
    finally:
        root.destroy()


def _run_native_images_dialog(initial_dir: str | None = None) -> list[str]:
    """Abre o diálogo nativo para seleção múltipla de imagens."""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        files = filedialog.askopenfilenames(
            parent=root,
            title="Selecione os Arquivos de Imagem",
            initialdir=initial_dir or str(get_user_documents_dir()),
            filetypes=[
                (
                    "Imagens Suportadas",
                    "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.tiff;*.tif;*.gif",
                ),
                ("PNG (*.png)", "*.png"),
                ("JPEG (*.jpg;*.jpeg)", "*.jpg;*.jpeg"),
                ("WEBP (*.webp)", "*.webp"),
                ("Todos os Arquivos", "*.*"),
            ],
        )
        return list(files) if files else []
    finally:
        root.destroy()


def _run_native_save_pptx_dialog(
    initial_dir: str | None = None, default_filename: str | None = None
) -> str | None:
    """Abre o diálogo nativo para salvar a apresentação PowerPoint."""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        dest = filedialog.asksaveasfilename(
            parent=root,
            title="Salvar Apresentação PowerPoint",
            initialdir=initial_dir or str(get_user_documents_dir()),
            initialfile=default_filename or "Apresentacao.pptx",
            defaultextension=".pptx",
            filetypes=[("Apresentação PowerPoint (*.pptx)", "*.pptx")],
        )
        return dest if dest else None
    finally:
        root.destroy()


async def ask_folder_async(initial_dir: str | None = None) -> str | None:
    """Executa a seleção de pasta em thread separada de forma assíncrona."""
    return await asyncio.to_thread(_run_native_folder_dialog, initial_dir)


async def ask_pdf_async(initial_dir: str | None = None) -> str | None:
    """Executa a seleção de PDF em thread separada de forma assíncrona."""
    return await asyncio.to_thread(_run_native_pdf_dialog, initial_dir)


async def ask_images_async(initial_dir: str | None = None) -> list[str]:
    """Executa a seleção de imagens em thread separada de forma assíncrona."""
    return await asyncio.to_thread(_run_native_images_dialog, initial_dir)


async def ask_save_pptx_async(
    initial_dir: str | None = None, default_filename: str | None = None
) -> str | None:
    """Executa o diálogo para salvar PPTX em thread separada de forma assíncrona."""
    return await asyncio.to_thread(_run_native_save_pptx_dialog, initial_dir, default_filename)
