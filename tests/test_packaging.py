"""Testes unitários para utilitários de empacotamento e versionamento automático."""

import importlib.util
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent


def _load_module_from_path(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível carregar o módulo: {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


version_bump = _load_module_from_path("version_bump", ROOT_DIR / "packaging" / "version_bump.py")
build_installer = _load_module_from_path(
    "build_installer", ROOT_DIR / "packaging" / "build_installer.py"
)


def test_calculate_next_version() -> None:
    """Verifica lógica de cálculo de SemVer."""
    assert version_bump.calculate_next_version("0.1.0", "patch") == "0.1.1"
    assert version_bump.calculate_next_version("0.1.0", "minor") == "0.2.0"
    assert version_bump.calculate_next_version("0.1.0", "major") == "1.0.0"
    assert version_bump.calculate_next_version("0.1.0", "0.3.5") == "0.3.5"

    with pytest.raises(ValueError):
        version_bump.calculate_next_version("0.1.0", "invalido")

    with pytest.raises(ValueError):
        version_bump.calculate_next_version("0.1", "patch")


def test_get_current_version() -> None:
    """Valida leitura da versão em pyproject.toml."""
    version = version_bump.get_current_version()
    assert version.count(".") == 2
    assert version == build_installer.get_version()


def test_inno_setup_template_validity() -> None:
    """Valida que o template do Inno Setup contém os placeholders e configurações necessárias."""
    formatted = build_installer.INNO_SETUP_TEMPLATE.replace("{version}", "0.1.0")
    assert 'MyAppVersion "0.1.0"' in formatted
    assert "OutputBaseFilename=PPT-Gen-Studio-Setup" in formatted
    assert 'MyAppExeName "PPT-Gen Studio.exe"' in formatted
