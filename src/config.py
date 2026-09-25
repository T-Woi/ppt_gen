"""Configurações centrais do PPT-Gen utilizando Pydantic-Settings, PyYAML e Python-Box."""

import sys
from pathlib import Path
from typing import Any

import yaml
from box import Box
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_project_root() -> Path:
    """Retorna o diretório raiz do projeto."""
    return Path(__file__).resolve().parent.parent


def resolve_web_dir() -> Path:
    """Localiza o diretório de recursos estáticos da interface web."""
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            for sub in ("web", "src/web", "ppt_gen/web"):
                candidate = Path(sys._MEIPASS) / sub
                if candidate.exists():
                    return candidate
        exe_parent = Path(sys.executable).parent
        for sub in (
            "web",
            "src/web",
            "_internal/web",
            "_internal/src/web",
            "_internal/ppt_gen/web",
        ):
            candidate = exe_parent / sub
            if candidate.exists():
                return candidate

    # Busca relativa ao diretório src/ (src/web)
    candidate = Path(__file__).resolve().parent / "web"
    if candidate.exists():
        return candidate

    # Fallback na raiz do projeto
    return get_project_root() / "src" / "web"


def load_yaml_presets(presets_path: Path | None = None) -> Box:
    """Carrega os presets do arquivo YAML e retorna um objeto Box com acesso via notação de ponto."""
    if presets_path is None:
        candidates = [
            Path(__file__).resolve().parent / "presets.yaml",
            get_project_root() / "src" / "presets.yaml",
            Path("presets.yaml"),
            get_project_root() / "presets.yaml",
        ]
        if getattr(sys, "frozen", False):
            if hasattr(sys, "_MEIPASS"):
                candidates.insert(0, Path(sys._MEIPASS) / "src" / "presets.yaml")
                candidates.insert(0, Path(sys._MEIPASS) / "presets.yaml")
            exe_parent = Path(sys.executable).parent
            candidates.insert(0, exe_parent / "_internal" / "src" / "presets.yaml")
            candidates.insert(0, exe_parent / "_internal" / "presets.yaml")
            candidates.insert(0, exe_parent / "src" / "presets.yaml")
            candidates.insert(0, exe_parent / "presets.yaml")

        for candidate in candidates:
            if candidate.exists():
                presets_path = candidate
                break

    if presets_path and presets_path.exists():
        with open(presets_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return Box(data, frozen_box=True)

    # Fallback caso não encontre o arquivo
    fallback_data: dict[str, Any] = {
        "app": {
            "name": "PPT-Gen Studio",
            "version": "0.1.0",
        },
        "defaults": {
            "aspect_ratio": "16:9",
            "fit_mode": "fit",
            "bg_color": "#FFFFFF",
            "pdf_dpi": 200,
            "theme": "dark",
        },
        "aspect_ratios": {
            "16:9": {"name": "Widescreen (16:9)", "width_inches": 13.333333, "height_inches": 7.5},
            "4:3": {"name": "Padrão (4:3)", "width_inches": 10.0, "height_inches": 7.5},
        },
        "fit_modes": {
            "fit": {"label": "Ajustar (Manter Proporção)"},
            "fill": {"label": "Preencher Slide"},
            "stretch": {"label": "Esticar ao Tamanho Total"},
        },
    }
    return Box(fallback_data, frozen_box=True)


class AppSettings(BaseSettings):
    """Configurações da aplicação gerenciadas via variáveis de ambiente e valores padrão."""

    model_config = SettingsConfigDict(env_prefix="PPT_GEN_", env_file=".env", extra="ignore")

    app_name: str = Field(default="PPT-Gen Studio", description="Nome da aplicação")
    debug: bool = Field(default=False, description="Modo debug ativado")

    default_aspect_ratio: str = Field(default="16:9", description="Proporção padrão (16:9 ou 4:3)")
    default_fit_mode: str = Field(default="fit", description="Modo de ajuste (fit, fill, stretch)")
    default_bg_color: str = Field(default="#FFFFFF", description="Cor de fundo padrão (hex)")
    default_pdf_dpi: int = Field(default=200, description="DPI padrão para rasterização de PDF")

    cache_max_thumbnails: int = Field(default=500, description="Limite de miniaturas no cache LRU")
    cache_max_preview_mb: int = Field(default=256, description="Limite de memória para previews")


settings = AppSettings()
presets: Box = load_yaml_presets()
