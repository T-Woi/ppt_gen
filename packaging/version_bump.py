"""PPT-Gen Studio - Script de Versionamento Automático (SemVer).

Permite incrementar versões automaticamente de forma sincronizada em:
1. pyproject.toml
2. src/__init__.py
3. src/presets.yaml
4. CHANGELOG.md (opcional)

Uso:
    uv run python packaging/version_bump.py patch   # 0.1.0 -> 0.1.1
    uv run python packaging/version_bump.py minor   # 0.1.0 -> 0.2.0
    uv run python packaging/version_bump.py major   # 0.1.0 -> 1.0.0
    uv run python packaging/version_bump.py 0.2.5   # define versão explícita
"""

import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def get_current_version() -> str:
    """Lê a versão atual definida no pyproject.toml."""
    pyproject = ROOT_DIR / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    if not match:
        raise ValueError("Campo 'version' não encontrado em pyproject.toml")
    return match.group(1)


def calculate_next_version(current: str, bump_type: str) -> str:
    """Calcula a próxima versão semântica (patch, minor, major ou explícita)."""
    parts = current.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise ValueError(f"Versão atual '{current}' não segue o formato SemVer X.Y.Z")

    major, minor, patch = (int(p) for p in parts)

    bump = bump_type.lower().strip()
    if bump == "patch":
        patch += 1
    elif bump == "minor":
        minor += 1
        patch = 0
    elif bump == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        # Verifica se passou uma versão explícita X.Y.Z
        if re.match(r"^\d+\.\d+\.\d+$", bump):
            return bump
        raise ValueError(
            f"Tipo de incremento inválido: '{bump_type}'. Use 'patch', 'minor', 'major' ou 'X.Y.Z'"
        )

    return f"{major}.{minor}.{patch}"


def update_pyproject(new_version: str) -> None:
    """Atualiza a versão no pyproject.toml."""
    pyproject = ROOT_DIR / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")
    updated = re.sub(
        r'^(version\s*=\s*["\'])[^"\']+(["\'])',
        rf"\g<1>{new_version}\g<2>",
        content,
        flags=re.MULTILINE,
    )
    pyproject.write_text(updated, encoding="utf-8")


def update_src_init(new_version: str) -> None:
    """Atualiza a versão no src/__init__.py."""
    init_file = ROOT_DIR / "src" / "__init__.py"
    if init_file.exists():
        content = init_file.read_text(encoding="utf-8")
        updated = re.sub(
            r'(__version__\s*=\s*["\'])[^"\']+(["\'])', rf"\g<1>{new_version}\g<2>", content
        )
        init_file.write_text(updated, encoding="utf-8")


def update_presets_yaml(new_version: str) -> None:
    """Atualiza a versão no src/presets.yaml."""
    presets_file = ROOT_DIR / "src" / "presets.yaml"
    if presets_file.exists():
        content = presets_file.read_text(encoding="utf-8")
        updated = re.sub(r'(version:\s*["\'])[^"\']+(["\'])', rf"\g<1>{new_version}\g<2>", content)
        presets_file.write_text(updated, encoding="utf-8")


def bump_version(bump_type: str) -> str:
    """Executa o incremento completo de versão em todos os arquivos sincronizados."""
    current = get_current_version()
    next_ver = calculate_next_version(current, bump_type)

    update_pyproject(next_ver)
    update_src_init(next_ver)
    update_presets_yaml(next_ver)

    print(f"[PPT-Gen] Versão atualizada: {current} -> {next_ver}")
    return next_ver


def main() -> None:
    """Função principal executada via CLI."""
    if len(sys.argv) < 2:
        print("Uso: python packaging/version_bump.py [patch|minor|major|X.Y.Z|--current]")
        print(f"Versão atual: {get_current_version()}")
        sys.exit(1)

    arg = sys.argv[1]
    if arg in ("--current", "-c", "current"):
        print(get_current_version())
        return

    bump_type = arg
    new_version = bump_version(bump_type)
    print("\nPara criar a tag e publicar o release:")
    print(f"  git commit -am 'chore(release): bump version to {new_version}'")
    print(f"  git tag v{new_version}")
    print("  git push origin main --tags")


if __name__ == "__main__":
    main()
