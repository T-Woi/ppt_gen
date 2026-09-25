"""PPT-Gen: Conversor Moderno de Imagens e PDF para PowerPoint (PPTX)."""

import sys

from config import presets, settings
from core.engines.pptx import build_presentation
from core.session import SessionManager
from main import cli_main

__version__ = "0.1.0"

# Compatibilidade caso algum módulo ainda use 'import ppt_gen'
sys.modules.setdefault("ppt_gen", sys.modules[__name__])

__all__ = [
    "SessionManager",
    "__version__",
    "build_presentation",
    "cli_main",
    "presets",
    "settings",
]
