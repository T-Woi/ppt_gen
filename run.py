"""PPT-Gen Studio - Execução Rápida em Modo de Desenvolvimento.

Inicia o backend Python de alta performance e abre automaticamente
a interface web no navegador padrão do usuário.
"""

import sys
from pathlib import Path

# Garante que 'src' esteja disponível no sys.path para execução direta sem compilação/build
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from main import cli_main  # noqa: E402

if __name__ == "__main__":
    cli_main()
