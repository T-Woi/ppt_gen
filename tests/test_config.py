"""Testes para o módulo de configurações centrais (config.py)."""

import sys
from pathlib import Path

from config import (
    AppSettings,
    get_project_root,
    load_yaml_presets,
    resolve_web_dir,
)


def test_get_project_root() -> None:
    """Verifica que a raiz do projeto é retornada corretamente."""
    root = get_project_root()
    assert (root / "src").exists()
    assert (root / "pyproject.toml").exists()


def test_resolve_web_dir_normal() -> None:
    """Testa a resolução do diretório web no ambiente de desenvolvimento normal."""
    web_dir = resolve_web_dir()
    assert web_dir.exists()
    assert (web_dir / "base.html").exists() or (web_dir / "index.html").exists()


def test_resolve_web_dir_frozen_meipass(tmp_path: Path, monkeypatch) -> None:
    """Testa a resolução quando executado empacotado com PyInstaller (_MEIPASS)."""
    fake_meipass = tmp_path / "meipass"
    fake_web = fake_meipass / "web"
    fake_web.mkdir(parents=True)

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(fake_meipass), raising=False)

    resolved = resolve_web_dir()
    assert resolved == fake_web


def test_resolve_web_dir_frozen_exe_parent(tmp_path: Path, monkeypatch) -> None:
    """Testa a resolução quando executado empacotado sem _MEIPASS (one-dir)."""
    fake_exe_dir = tmp_path / "dist_app"
    fake_web = fake_exe_dir / "_internal" / "web"
    fake_web.mkdir(parents=True)

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    # Remove _MEIPASS se existir
    if hasattr(sys, "_MEIPASS"):
        monkeypatch.delattr(sys, "_MEIPASS")
    monkeypatch.setattr(sys, "executable", str(fake_exe_dir / "ppt-gen.exe"))

    resolved = resolve_web_dir()
    assert resolved == fake_web


def test_resolve_web_dir_fallback(tmp_path: Path, monkeypatch) -> None:
    """Testa fallback quando caminho padrão não existe."""
    # Simula diretório inexistente em __file__
    fake_file = tmp_path / "somewhere" / "config.py"
    monkeypatch.setattr("config.__file__", str(fake_file))
    resolved = resolve_web_dir()
    assert "src" in str(resolved) and "web" in str(resolved)


def test_load_yaml_presets_normal() -> None:
    """Testa o carregamento dos presets padrão do arquivo YAML."""
    presets = load_yaml_presets()
    assert "defaults" in presets
    assert presets.defaults.aspect_ratio == "16:9"
    assert "16:9" in presets.aspect_ratios


def test_load_yaml_presets_fallback(tmp_path: Path) -> None:
    """Testa se o fallback interno em código funciona quando o arquivo YAML não existe."""
    inexistent = tmp_path / "nao_existe.yaml"
    presets = load_yaml_presets(presets_path=inexistent)
    assert "app" in presets
    assert presets.app.name == "PPT-Gen Studio"
    assert presets.defaults.fit_mode == "fit"


def test_load_yaml_presets_frozen(tmp_path: Path, monkeypatch) -> None:
    """Testa a busca de presets.yaml quando em ambiente frozen."""
    fake_meipass = tmp_path / "meipass"
    fake_meipass.mkdir(parents=True)
    fake_yaml = fake_meipass / "presets.yaml"
    fake_yaml.write_text("app:\n  name: Teste Frozen\n", encoding="utf-8")

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(fake_meipass), raising=False)

    presets = load_yaml_presets()
    assert presets.app.name == "Teste Frozen"


def test_app_settings_defaults() -> None:
    """Valida configurações de AppSettings."""
    cfg = AppSettings()
    assert cfg.app_name == "PPT-Gen Studio"
    assert cfg.default_aspect_ratio == "16:9"
    assert cfg.default_pdf_dpi == 200
